import { test, expect } from '@playwright/test'

test.describe('home page',  () => {
    test('loads correctly with title', async ({ page }) => {
        await page.goto('/');
        const pageHeading = page.getByRole('heading', { name: 'League Standings '});
        await expect(pageHeading).toBeVisible();
    });

});