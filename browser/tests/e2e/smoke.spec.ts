import { expect, test } from '@playwright/test';

test('briefs the person and records one honest A/B/C choice', async ({ page }) => {
  await page.goto('/');
  await expect(page).toHaveTitle('Pilot Puppy');
  await expect(page.getByRole('heading', { name: 'Pilot Puppy' })).toBeVisible();
  await expect(page.getByRole('heading', { name: 'Publish release notes people can trust.' })).toBeVisible();
  await expect(page.getByText('The goal', { exact: true })).toBeVisible();
  await expect(page.getByText('Right now', { exact: true })).toBeVisible();
  await expect(page.getByText("What's new", { exact: true })).toBeVisible();
  await expect(page.getByText('Pick what happens next', { exact: true })).toBeVisible();
  await expect(page.getByText('This is the multiple-choice step: pick A, B, or C.', { exact: true })).toBeVisible();
  await expect(page.getByRole('button', { name: /A Ship now/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /B Run a cold review/ })).toBeVisible();
  await expect(page.getByRole('button', { name: /C Hold the release/ })).toBeVisible();
  await page.getByRole('button', { name: /B Run a cold review/ }).click();
  await expect(page.getByText('Saved. Pilot Puppy is ready for the next step.')).toBeVisible();
});

test('exposes proof without implementation machinery', async ({ page }) => {
  await page.goto('/');
  await page.getByText('What we checked', { exact: true }).click();
  await expect(page.getByText('Browser contract tests pass.')).toBeVisible();
  await expect(page.getByText('tests/test_browser.py')).toBeVisible();
  await expect(page.locator('body')).not.toContainText('provider');
  await expect(page.locator('body')).not.toContainText('transcript');
});

test('makes the four work shapes visible without routing or launching work', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByText('How Pilot Puppy helps', { exact: true })).toBeVisible();
  await expect(page.getByText('Make a plan', { exact: true })).not.toBeVisible();
  await page.getByText('How Pilot Puppy helps', { exact: true }).click();
  await expect(page.getByText('When the next step is unclear')).toBeVisible();
  await expect(page.getByText('Make a plan', { exact: true })).toBeVisible();
  await expect(page.getByText('A small, focused change')).toBeVisible();
  await expect(page.getByText('Build it', { exact: true })).toBeVisible();
  await expect(page.getByText('A problem we can repeat')).toBeVisible();
  await expect(page.getByText('Find the fix', { exact: true })).toBeVisible();
  await expect(page.getByText('A big change that needs extra checking')).toBeVisible();
  await expect(page.getByText('Handle the hard part', { exact: true })).toBeVisible();
  await expect(page.getByText('Pilot Puppy waits for you to choose before anything starts.')).toBeVisible();
});
