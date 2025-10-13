import { test, expect } from '@playwright/test'
import { hasUncaughtExceptionCaptureCallback } from 'process';

test.describe('standings',  () => {
    
    // constants for standings tests
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

    const expectedPacificTeams = [
        'Edmonton Oilers',
        'Calgary Flames',
        'Seattle Kraken',
        'Los Angeles Kings',
        'Vegas Golden Knights',
        'Vancouver Canucks',
        'Anaheim Ducks',
        'San Jose Sharks'
    ].sort();

    const expectedCentralTeams = [
        'Colorado Avalanche',
        'Dallas Stars',
        'Nashville Predators',
        'Minnesota Wild',
        'Winnipeg Jets',
        'St. Louis Blues',
        'Utah Mammoth',
        'Chicago Blackhawks'
    ].sort();

    const expectedMetroTeams = [
        'Carolina Hurricanes',
        'Washington Capitals',
        'Pittsburgh Penguins',
        'New York Rangers',
        'Columbus Blue Jackets',
        'New Jersey Devils',
        'Philadelphia Flyers',
        'New York Islanders'
    ].sort();

    const westernConferenceTeams = (expectedCentralTeams.concat(expectedPacificTeams)).sort();
    const easternConferenceTeams = (expectedMetroTeams.concat(expectedAtlanticTeams)).sort();

    // tests 
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

        // get teams in atlantic
        const atlantic = page.locator('.division-table', { hasText: 'Atlantic' });
        const atlanticTeamCells = atlantic.locator('tbody tr td:nth-child(2)');
        const atlanticTeams = (await atlanticTeamCells.allTextContents()).map(name => name.trim()).sort();

        // get team in pacific
        const pacific = page.locator('.division-table', { hasText: 'Pacific' });
        const pacificTeamCells = pacific.locator('tbody tr td:nth-child(2)');
        const pacificTeams = (await pacificTeamCells.allTextContents()).map(name => name.trim()).sort();

        // get team in metropolitan
        const metropolitan = page.locator('.division-table', { hasText: 'Metropolitan' });
        const metroTeamCells = metropolitan.locator('tbody tr td:nth-child(2)');
        const metroTeams = (await metroTeamCells.allTextContents()).map(name => name.trim()).sort();

        // get team in central
        const central = page.locator('.division-table', { hasText: 'Central' });
        const centralTeamCells = central.locator('tbody tr td:nth-child(2)');
        const centralTeams = (await centralTeamCells.allTextContents()).map(name => name.trim()).sort();

        // check if lists contain the div teams 
        expect(atlanticTeams).toEqual(expectedAtlanticTeams);
        expect(pacificTeams).toEqual(expectedPacificTeams);
        expect(metroTeams).toEqual(expectedMetroTeams);
        expect(centralTeams).toEqual(expectedCentralTeams);
    });

    // conference standings
    test('conference standings western default is correct', async ({ page }) => {
        await page.goto('/');

        // check the default on page load
        const selectedOptionValue = await page.getByRole('combobox').inputValue();
        expect(selectedOptionValue).toBe('Western');

        // get teams conference
        const conference = page.locator('#conference_standings table');
        const conferenceTeamCells = conference.locator('tbody tr td:nth-child(2)');
        const conferenceTeams = (await conferenceTeamCells.allTextContents()).map(name => name.trim()).sort();
        
        // check western teams are correct
        expect(conferenceTeams).toEqual(westernConferenceTeams);        
    });

    test('conference standings eastern are correct', async ({ page }) => {
        await page.goto('/');

        // check option selection changes
        await page.getByRole('combobox').selectOption('Eastern');
        const selectedOptionValue = await page.getByRole('combobox').inputValue();
        expect(selectedOptionValue).toBe('Eastern');

        // wait for the table to populate teams
        await page.locator('#conference_standings table td', { hasText: 'Toronto Maple Leafs' }).waitFor();

        // get teams conference
        const conference = page.locator('#conference_standings table');
        const conferenceTeamCells = conference.locator('tbody tr td:nth-child(2)');
        const conferenceTeams = (await conferenceTeamCells.allTextContents()).map(name => name.trim()).sort();
        
        // check eastern teams are correct
        expect(conferenceTeams).toEqual(easternConferenceTeams);        
    });

});