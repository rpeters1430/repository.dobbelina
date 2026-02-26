import { test, expect } from "@playwright/test";

test("stripchat basic flow", async ({ page }) => {
  await page.goto("https://stripchat.com/");

  const ageButton = page.getByRole("button", { name: "I'm Over" });
  if (await ageButton.isVisible().catch(() => false)) {
    await ageButton.click();
  }

  await page
    .getByRole("link", { name: /Live Sex Cam Show/i })
    .first()
    .click();

  await expect(page).toHaveURL(/stripchat\.com/);
});
