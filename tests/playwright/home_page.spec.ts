import { test, expect } from '@playwright/test'

test.describe('home page',  () => {
    
    test('loads correctly with title', async ({ page }) => {
        await page.goto('/');
        const pageHeading = page.getByRole('heading', { name: 'League Standings '});
        await expect(pageHeading).toBeVisible();
    });

    test('navbar link Team Insights loads on click', async ({ page }) => {
        await page.goto('http://127.0.0.1:8000/');
        const teamInsightsPromise = page.waitForEvent('load');
        await page.getByRole('link', { name: 'Team Insights' }).click();
        
        const pageTeamInsights = await teamInsightsPromise;
        await pageTeamInsights.waitForLoadState('domcontentloaded');
        
        // check link changes
        await expect(pageTeamInsights.url()).toContain('/stats')

        // check for proper page header
        const pageHeading = await pageTeamInsights.locator('h2').allTextContents();
        expect(pageHeading[0]).toEqual('Team Insights');
    });

    test('navbar link Player Eval loads on click', async ({ page }) => {
        await page.goto('http://127.0.0.1:8000/');
        const playerEvalPromise = page.waitForEvent('load');
        await page.getByRole('link', { name: 'Player Evaluation' }).click();
        
        const pagePlayerEval = await playerEvalPromise;
        await pagePlayerEval.waitForLoadState('domcontentloaded');
        
        // check link changes
        await expect(pagePlayerEval.url()).toContain('/eval')

        // check for proper page header
        const pageHeading = await pagePlayerEval.locator('h2').allTextContents();
        expect(pageHeading[0]).toEqual('Player Evaluation');
    });

    test('navbar link Rink Plot loads on click', async ({ page }) => {
        await page.goto('http://127.0.0.1:8000/');
        const rinkPlotPromise = page.waitForEvent('load');
        await page.getByRole('link', { name: 'Rink Plot' }).click();
        
        const pageRinkPlot = await rinkPlotPromise;
        await pageRinkPlot.waitForLoadState('domcontentloaded');
        
        // check link changes
        await expect(pageRinkPlot.url()).toContain('/rink')

        // check for proper page header
        const pageHeading = await pageRinkPlot.locator('h1').allTextContents();
        expect(pageHeading[0]).toEqual('Shot Chart on Rink');
    });

    test('navbar link League Standings loads on click from other link', async ({ page }) => {
        await page.goto('http://127.0.0.1:8000/rink/');
        const leagueStandingsPromise = page.waitForEvent('load');
        await page.getByRole('link', { name: 'League Standings' }).click();
        
        const pageLeagueStandings = await leagueStandingsPromise;
        await pageLeagueStandings.waitForLoadState('domcontentloaded');
        
        // check link changes
        await expect(pageLeagueStandings.url()).toEqual('http://127.0.0.1:8000/')

        // check for proper page header
        const pageHeading = await pageLeagueStandings.locator('h2').allTextContents();
        expect(pageHeading[0]).toEqual('League Standings');
    });

});