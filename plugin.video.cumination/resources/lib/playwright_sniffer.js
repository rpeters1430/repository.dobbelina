const { chromium } = require('@playwright/test');
const fs = require('fs');

async function sniff(url, playSelectors = [], preferredExtension = null, excludeDomains = []) {
    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    });
    const page = await context.newPage();

    let foundUrl = null;
    const allVideoUrls = [];

    page.on('response', response => {
        const rUrl = response.url().toLowerCase();
        if ((rUrl.includes('.mp4') || rUrl.includes('.m3u8') || rUrl.includes('.m4s')) && 
            !['/thumbs/', '/images/', '.jpg', '.png', '/thumb/', '/image/'].some(x => rUrl.includes(x))) {
            
            if (excludeDomains.some(domain => rUrl.includes(domain.toLowerCase()))) {
                return;
            }

            if (!allVideoUrls.includes(response.url())) {
                allVideoUrls.push(response.url());
                if (preferredExtension && rUrl.includes(preferredExtension.toLowerCase())) {
                    foundUrl = response.url();
                } else if (!foundUrl) {
                    foundUrl = response.url();
                }
            }
        }
    });

    try {
        await page.goto(url, { waitUntil: 'load', timeout: 30000 });
        await page.waitForTimeout(3000);

        if (playSelectors.length > 0) {
            for (const selector of playSelectors) {
                if (foundUrl) break;
                try {
                    const elements = page.locator(selector);
                    const count = await elements.count();
                    for (let i = 0; i < count; i++) {
                        const elem = elements.nth(i);
                        if (await elem.isVisible()) {
                            await elem.click({ force: true });
                            await page.waitForTimeout(3000);
                            if (foundUrl) break;
                        }
                    }
                } catch (e) {}
            }
        }

        // Wait a bit more
        for (let i = 0; i < 10; i++) {
            if (foundUrl) break;
            await page.waitForTimeout(500);
        }

        if (foundUrl) {
            console.log(JSON.stringify({ url: foundUrl }));
        } else {
            console.log(JSON.stringify({ error: 'Not found' }));
        }

    } catch (e) {
        console.log(JSON.stringify({ error: e.message }));
    } finally {
        await browser.close();
    }
}

const args = JSON.parse(process.argv[2]);
sniff(args.url, args.playSelectors, args.preferredExtension, args.excludeDomains);
