#!/usr/bin/env node

// NOTE: "await" is used many times in this script. This means that it will wait until its called
// function is complete before it runs. Asynchronous calls are being made in this script, and to
// prevent race conditions, the await statement is made so that there are less errors that could happen.
// "await" is called whenever page navigation, writing, or content is being rendered.

const puppeteer = require('puppeteer');
const fs = require('fs').promises;

// URLs for the two users.
const victim_url = "http://10.0.1.1/xss_practice.php?auth=z8pivtWHdXKRS9ks2RyqSQsuM0aaxyFy";
const umdsec_url = "http://10.0.1.1/xss_practice.php?auth=UMsVqXewPzULMBUfb71mhXeu8ai2ruHl";

// This is the "main" function that gets called.
async function run(step) {
    // Create a browser and a page.
    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    // If this is Step 2, add a page.on handler, which prints the console.log information.
    if (step == 2) {
        page.on('console', msg => {
            // There is an issue here with 404 errors occurring, despite the page being accessed properly.
            // If there are any errors occurring in this script, comment out this "if" statement.
            if (!msg.text().includes('404')) {
                console.log(msg.text());
            }
        });
    }

    // Accessing the website at a given URL. Must be either umdsec_url or victim_url.
    async function accessWebsite(url) {
        // If there's a request error (which there shouldn't), then print the reason.
        // This may affect the section_2.py script.
        page.on('requestfailed', request => {
            console.log(`${request.url()} failed to load. Reason: ${request.failure().errorText}`);
        });

        try {
            // Accesses the webpage, assigns response. Wait until "networkidle2" means the function is
            // complete when no more than two calls are made within 500ms.
            const response = await page.goto(url, { waitUntil: 'networkidle2' });
            if (response.ok()) {
                // console.log("Successfully accessed " + url);
                return await page.content();
            } else {
                // console.log("Error accessing " + url);
                return "Error";
            }
        } catch (error) {
            // console.log("Error accessing " + url + ": " + error.message);
            return "Error";
        }
    }

    // Logic for handling steps
    if (step === 2) {
        const content = await accessWebsite(umdsec_url);
        if (content === "Error") {
            await browser.close();
            process.exit(2);
        }

        // Write content to file
        try {
            await fs.writeFile('/home/.checker/responses/step_2_response.txt', content);
            // console.log("File successfully written.");
        }

        catch (e) {
            // console.log("File write error: " + e);
        }
    }

    else if (step === 3) {
        // Gather the responses from the three websites being accessed.
        // content1 and content3 will be compared at the end. If they're different,
        // then this step is passed.
        const content1 = await accessWebsite(victim_url);
        const content2 = await accessWebsite(umdsec_url);
        const content3 = await accessWebsite(victim_url);

        // Creating a response file which will be saved in case the student runs the "auto-grader" later.
        try {
            await fs.writeFile('/home/.checker/responses/step_3_response.txt', content1);
            await fs.appendFile('/home/.checker/responses/step_3_response.txt', "\n-DIVIDER-\n");
            await fs.appendFile('/home/.checker/responses/step_3_response.txt', content3);
        }

        catch (e) {
            console.log("File write error: " + e);
            process.exit(2)
        }

        // In case the student is running this step without the "keep work" boolean, then the rest
        // of the check can easily be made here. Just compare the two strings, then return a value.
        if (content1 !== content3) {
            process.exit(0);
        }

        else {
            process.exit(1);
        }
    }

    else if (step === 4) {
        // This will be similar to Step 3, but in reverse. Access the umdsec account, save
        // the response, then access victim's URL. Its URL should've been posted to umdsec.
        // Check if content1 and content3 are different later.
        const content1 = await accessWebsite(umdsec_url);
        const content2 = await accessWebsite(victim_url);
        const content3 = await accessWebsite(umdsec_url);
        // Creating a response file which will be saved in case the student runs the "auto-gr>
        try {
            await fs.writeFile('/home/.checker/responses/step_4_response.txt', content1);
            await fs.appendFile('/home/.checker/responses/step_4_response.txt', "\n-DIVIDER-\n");
            await fs.appendFile('/home/.checker/responses/step_4_response.txt', content3);
        }

        catch (e) {
            console.log("File write error: " + e);
            process.exit(2)
        }

        // Like Step 3, in case the student is running this step without the "keep work"
        // boolean, then the check can easily be made here. First, compare the two strings.
        // They must be different, since a response should've been made to umdsec.
        if (content1 !== content3) {
            // Now, check to see if content3 has the victim's URL in it.
            if (content3.includes(victim_url)) {
                process.exit(0);
            }

            // Otherwise, exit with 0.
                process.exit(1);
        }

        else {
            process.exit(1);
        }
    }

    // Close the browser
    await browser.close();
}

// Check if the usage is being called correctly.
if ((process.argv).length != 3) {
    console.log("Usage: node ./section_2.js <step_num>");
    process.exit(2);
}

// Get the step number. Need to "parseInt" to decimal. Otherwise, it won't work.
const step = parseInt(process.argv[2], 10);

// Run the "run" command above.
run(step).catch(err => {
//    console.error(err);
    process.exit(2);
});
