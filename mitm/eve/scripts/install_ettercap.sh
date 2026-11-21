#!/bin/bash
# install_ettercap.sh
#
# Standalone, one-time installer: builds ettercap from the GitHub
# master branch (for a fix not yet in Ubuntu's apt release) and
# installs it system-wide. Meant to be run ONCE BY HAND on eve before
# taking an OS image/snapshot to distribute to students - it is NOT
# part of the per-swap-in install_eve script, because the build is
# slow enough to make that script look frozen.
#
# Usage:  sudo ./install_ettercap.sh
#
# Safe to re-run: it wipes and rebuilds its own source trees each time.

if [ "$(id -u)" -ne 0 ]; then
	echo "Please run this as root (sudo ./install_ettercap.sh)."
	exit 1
fi

LOG="/var/log/ettercap-install.log"
echo "=== install_ettercap.sh starting $(date) ===" | tee "$LOG"

log() {
	echo "$1" | tee -a "$LOG"
}

# --- 1. Make sure nothing else is fighting us for the dpkg lock -----------
log ">>> Quieting apt's periodic timers (apt-daily, unattended-upgrades)..."
systemctl stop apt-daily.service apt-daily-upgrade.service unattended-upgrades.service >> "$LOG" 2>&1
systemctl disable --now apt-daily.timer apt-daily-upgrade.timer >> "$LOG" 2>&1

LOCK_WAIT=0
while [ $LOCK_WAIT -lt 300 ] && { fuser /var/lib/dpkg/lock-frontend >/dev/null 2>&1 || fuser /var/lib/apt/lists/lock >/dev/null 2>&1; }
do
	log "    waiting for existing apt/dpkg process to finish... (${LOCK_WAIT}s)"
	sleep 5
	LOCK_WAIT=$((LOCK_WAIT + 5))
done

# -o DPkg::Lock::Timeout=300 is a safety net for anything that still
# briefly grabs the lock after the above.
APT="apt-get -o DPkg::Lock::Timeout=300 -y"

# --- 2. Install ettercap's build dependencies ------------------------------
log ""
log ">>> Installing build dependencies..."
$APT update >> "$LOG" 2>&1

for PKG in git build-essential cmake bison flex debhelper libgtk3.0-dev \
           libltdl3-dev libncurses-dev libncurses5-dev libnet1-dev \
           libpcap-dev libssl-dev libcurl4-openssl-dev ghostscript
do
	log "    installing $PKG..."
	$APT install "$PKG" >> "$LOG" 2>&1
done

# --- 3. Build legacy PCRE1 from source, if needed --------------------------
# Ettercap's core filter engine (src/ec_filter.c) calls the classic
# PCRE1 API (pcre_compile/pcre_free/pcre_study) unconditionally, not
# PCRE2. This Ubuntu release dropped the libpcre3-dev package with no
# replacement, so build PCRE 8.45 (the final PCRE1 release) from
# source. Skipped entirely if pcre.h is already present.
if [ ! -f /usr/local/include/pcre.h ] && [ ! -f /usr/include/pcre.h ]; then
	log ""
	log ">>> libpcre3-dev unavailable via apt; building PCRE 8.45 from source..."

	PCRE_SRC="/usr/local/src/pcre-8.45"
	PCRE_TGZ="/usr/local/src/pcre-8.45.tar.gz"
	rm -rf "$PCRE_SRC" "$PCRE_TGZ"
	PCRE_OK=1

	log "    downloading..."
	if ! curl -L -o "$PCRE_TGZ" "https://downloads.sourceforge.net/project/pcre/pcre/8.45/pcre-8.45.tar.gz" >> "$LOG" 2>&1; then
		log "ERROR: PCRE 8.45 download failed - see $LOG"
		PCRE_OK=0
	elif ! tar -xzf "$PCRE_TGZ" -C /usr/local/src >> "$LOG" 2>&1; then
		log "ERROR: PCRE 8.45 extract failed - see $LOG"
		PCRE_OK=0
	fi

	if [ $PCRE_OK -eq 1 ]; then
		pushd "$PCRE_SRC" > /dev/null
		log "    configuring..."
		if ! ./configure --prefix=/usr/local >> "$LOG" 2>&1; then
			log "ERROR: PCRE 8.45 configure failed - see $LOG"
			PCRE_OK=0
		else
			log "    building (this can take a few minutes)..."
			if ! make -j"$(nproc)" >> "$LOG" 2>&1; then
				log "ERROR: PCRE 8.45 make failed - see $LOG"
				PCRE_OK=0
			else
				log "    installing..."
				if ! make install >> "$LOG" 2>&1; then
					log "ERROR: PCRE 8.45 make install failed - see $LOG"
					PCRE_OK=0
				else
					ldconfig
				fi
			fi
		fi
		popd > /dev/null
	fi

	if [ $PCRE_OK -eq 0 ]; then
		log "WARNING: PCRE 8.45 build failed - ettercap's build will likely fail on ec_filter.c"
	else
		log "    PCRE 8.45 installed OK."
	fi
fi

# --- 4. Build and install ettercap from GitHub master -----------------------
log ""
log ">>> Cloning ettercap (GitHub master)..."

ETTERCAP_SRC="/usr/local/src/ettercap"
rm -rf "$ETTERCAP_SRC"
ETTERCAP_OK=1

if ! git clone https://github.com/Ettercap/ettercap.git "$ETTERCAP_SRC" >> "$LOG" 2>&1; then
	log "ERROR: ettercap git clone failed - see $LOG"
	ETTERCAP_OK=0
fi

if [ $ETTERCAP_OK -eq 1 ]; then
	mkdir -p "$ETTERCAP_SRC/build"
	pushd "$ETTERCAP_SRC/build" > /dev/null

	log ">>> Configuring (cmake)..."
	# -DENABLE_GTK=Off -DENABLE_CURSES=On : text/curses UI only, same
	#   as the ettercap-text-only package this replaces.
	# -DENABLE_GEOIP=Off : this lab doesn't need geolocation, and it
	#   avoids pulling in libmaxminddb-dev as another build dependency.
	if ! cmake -DENABLE_GTK=Off -DENABLE_CURSES=On -DENABLE_GEOIP=Off .. >> "$LOG" 2>&1; then
		log "ERROR: ettercap cmake configure failed - see $LOG"
		ETTERCAP_OK=0
	else
		log ">>> Building (this is the slow part - can take 10+ minutes)..."
		if ! make -j"$(nproc)" >> "$LOG" 2>&1; then
			log "ERROR: ettercap make failed - see $LOG"
			ETTERCAP_OK=0
		else
			log ">>> Installing..."
			if ! make install >> "$LOG" 2>&1; then
				log "ERROR: ettercap make install failed - see $LOG"
				ETTERCAP_OK=0
			else
				ldconfig
			fi
		fi
	fi
	popd > /dev/null
fi

# --- 5. Fix the etter.conf path and set a usable connection_buffer --------
# make install (default /usr/local prefix) installs etter.conf to
# /usr/local/etc/ettercap/etter.conf - NOT /etc/ettercap/etter.conf,
# which is where every generic ettercap tutorial (and the lab manual
# itself) tells you to edit it. Symlink the standard path to the real
# one so that guidance just works. Confirmed via:
#   strace -f -e trace=openat,open ettercap -C -i <iface> 2>&1 | grep etter.conf
if [ $ETTERCAP_OK -eq 1 ]; then
	REAL_CONF="/usr/local/etc/ettercap/etter.conf"
	if [ -f "$REAL_CONF" ]; then
		log ""
		log ">>> Linking /etc/ettercap/etter.conf -> $REAL_CONF"
		mkdir -p /etc/ettercap
		ln -sf "$REAL_CONF" /etc/ettercap/etter.conf

		# The upstream source tree's etter.conf ships with
		# connection_buffer unset/0, which disables retroactive
		# viewing in View > Connections for anything already closed
		# by the time you open it (TX/RX counters still show real
		# bytes, but the content pane is empty). A normal apt
		# package's conffile ships with a sane default already; set
		# one here so building from source behaves the same way.
		if grep -q "^connection_buffer" "$REAL_CONF"; then
			sed -i 's/^connection_buffer.*/connection_buffer = 65536/' "$REAL_CONF"
		elif grep -q "^#.*connection_buffer" "$REAL_CONF"; then
			sed -i 's/^#.*connection_buffer.*/connection_buffer = 65536/' "$REAL_CONF"
		else
			echo "connection_buffer = 65536" >> "$REAL_CONF"
		fi
		log "    connection_buffer set to 65536 in $REAL_CONF"
	else
		log "WARNING: expected $REAL_CONF but didn't find it - etter.conf path/symlink and connection_buffer were NOT set, do it by hand"
	fi
fi

log ""
if [ $ETTERCAP_OK -eq 1 ]; then
	log ">>> SUCCESS. Installed version:"
	ettercap --version 2>&1 | tee -a "$LOG"
	log ""
	log "You can now run, e.g.: ettercap -C -i <interface>"
	log "Config file (both paths work): /etc/ettercap/etter.conf -> $REAL_CONF"
	exit 0
else
	log ">>> FAILED. See $LOG for details."
	exit 1
fi
