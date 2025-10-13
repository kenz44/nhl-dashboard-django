import { test, expect } from '@playwright/test'

test.describe('team insights page',  () => {

    test('loads player roster for a selected team', async ({ page }) => {
        await page.goto('/stats/');
        await expect(page.getByRole('heading', { name: 'Team Insights' })).toBeVisible();

        // select a team
        await page.getByRole('combobox').selectOption('EDM');
        const selectedOptionValue = await page.getByRole('combobox').inputValue();
        expect(selectedOptionValue).toBe('EDM');

        // wait for table to load
        await page.getByText(/Skater Stats/).isVisible();

        // check for a player 
        const tableData = page.locator('h3:has-text("Skater Stats") + div table');
        // wait for table to exist
        await tableData.locator('tbody tr').first().waitFor({ state: 'visible' });
        const rows = tableData.locator('tbody tr');

        // cehck that rows exist 
        const numRows = await rows.count();
        expect(numRows).toBeGreaterThan(0);

        const firstPlayer = await rows.nth(0).locator('td:nth-child(2)').textContent();
        expect(firstPlayer).not.toBeNull();
    });

    test('loads team logo image in background on selection', async ({ page }) => {
        await page.goto('/stats/');
        await expect(page.getByRole('heading', { name: 'Team Insights' })).toBeVisible();

        // select a team
        await page.getByRole('combobox').selectOption('EDM');
        const selectedOptionValue = await page.getByRole('combobox').inputValue();
        expect(selectedOptionValue).toBe('EDM');

        // wait for table to exist
        const tableData = page.locator('h3:has-text("Skater Stats") + div table');
        await tableData.locator('tbody tr').first().waitFor({ state: 'visible' });

        // check background img on div with that style
        const backgroundDiv = page.locator('div[style*="background-image"]');
        const backgroundImg = await backgroundDiv.evaluate(el => getComputedStyle(el).backgroundImage);
        expect(backgroundImg).toContain('EDM_light.svg');
    });

});