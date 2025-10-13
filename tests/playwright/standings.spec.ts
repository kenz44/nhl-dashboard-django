import { test, expect } from '@playwright/test'

test.describe('home page',  () => {

    test('division standings grid renders', async ({ page }) => {
        await page.goto('/');

        // get all div rows, there should be 2
        const divRows = page.locator('.division-row');
        await expect(divRows).toHaveCount(2);

        // get all tables in rows, there should be 2
        const row1Tables = divRows.nth(0).locator('.division-table');
        const row2Tables = divRows.nth(1).locator('.division-table');

        await expect(row1Tables).toHaveCount(2);
        await expect(row2Tables).toHaveCount(2);

        // check row 1 has Atlantic, Metropolitan
        // check row 2 has Central, Pacific
        const divNames1 = await row1Tables.locator('h3').allTextContents();
        const divNames2 = await row2Tables.locator('h3').allTextContents();

        expect(divNames1).toEqual(['Atlantic', 'Metropolitan']);
        expect(divNames2).toEqual(['Central', 'Pacific'])
    });

    test('division standings show correct teams', async ({ page }) => {
        await page.goto('/');

        // get teams in each div
        const atlantic = page.locator('.division-table', { hasText: 'Atlantic' });
        const teamCells = atlantic.locator('tbody tr td:nth-child(2)');
        const teamNames = (await teamCells.allTextContents()).map(name => name.trim()).sort();

        // check if lists contain the div teams 
        const expectedAtlanticTeams = [
            'Florida Panthers', 
            'Boston Bruins', 
            'Toronto Maple Leafs', 
            'Ottawa Senators', 
            'Montréal Canadiens', 
            'Tampa Bay Lightning', 
            'Detroit Red Wings', 
            'Buffalo Sabres'
        ].sort();

        expect(teamNames).toEqual(expectedAtlanticTeams);
    });

});