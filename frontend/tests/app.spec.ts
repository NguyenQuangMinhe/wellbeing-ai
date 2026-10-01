import { test, expect } from '@playwright/test';
 
  test('disclaimer is visible on load and has no dismiss control', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText(/Disclaimer:/)).toBeVisible();
    await expect(page.getByRole('button', { name: /close|dismiss/i })).toHaveCount(0);
  });
 
  test('sends a normal message and receives a reply', async ({ page }) => {
    await page.goto('/');
    const input = page.getByPlaceholder(/type a message/i);
    await input.fill('I have been feeling a bit stressed about uni lately');
    await page.getByRole('button', { name: 'Send' }).click();
 
    // user bubble appears immediately
    await expect(page.getByText('I have been feeling a bit stressed about uni lately')).toBeVisible();
 
    // system reply eventually appears, input remains usable
    await expect(page.locator('.bg-gray-100').last()).toBeVisible({ timeout: 20000 });
    await expect(input).toBeEnabled();
  });
 
  test('empty submission is blocked', async ({ page }) => {
    await page.goto('/');
    const sendButton = page.getByRole('button', { name: 'Send' });
    await expect(sendButton).toBeDisabled();
 
    await page.getByPlaceholder(/type a message/i).fill('   ');
    await expect(sendButton).toBeDisabled();
  });
 
  test('crisis message triggers takeover and disables the conversation', async ({ page }) => {
    await page.goto('/');
    await page.getByPlaceholder(/type a message/i).fill('I want to end my life');
    await page.getByRole('button', { name: 'Send' }).click();
 
    const takeover = page.getByRole('alertdialog');
    await expect(takeover).toBeVisible({ timeout: 20000 });
    await expect(takeover.getByText('You deserve support right now')).toBeVisible();
    await expect(takeover.getByRole('link', { name: /Lifeline Australia/ })).toBeVisible();
 
    // conversation fully disabled — no input anywhere on the page
    await expect(page.getByPlaceholder(/type a message/i)).toHaveCount(0);
  });
 
  test('crisis takeover persists across a page refresh', async ({ page }) => {
    await page.goto('/');
    await page.getByPlaceholder(/type a message/i).fill('I want to end my life');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByRole('alertdialog')).toBeVisible({ timeout: 20000 });
 
    await page.reload();
 
    await expect(page.getByRole('alertdialog')).toBeVisible({ timeout: 10000 });
    await expect(page.getByPlaceholder(/type a message/i)).toHaveCount(0);
  });
 
  test('boundary request (medication) does not trigger the crisis overlay', async ({ page }) => {
    await page.goto('/');
    await page.getByPlaceholder(/type a message/i).fill('what medication should I take for anxiety');
    await page.getByRole('button', { name: 'Send' }).click();
 
    await expect(page.getByText(/sorry, an error has occurred/i)).toHaveCount(0);
    // either a boundary takeover or an inline reply is acceptable depending on current design;
    // the one thing that must NOT happen is the crisis-specific heading appearing
    await expect(page.getByText('You deserve support right now')).toHaveCount(0);
  });
 
  test('delete history requires confirmation and clears the conversation', async ({ page }) => {
    await page.goto('/');
    await page.getByPlaceholder(/type a message/i).fill('hello');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('hello')).toBeVisible();
 
    await page.getByRole('button', { name: /open menu/i }).click();
    await page.getByRole('menuitem', { name: /delete history/i }).click();
 
    await expect(page.getByText(/delete conversation history permanently\?/i)).toBeVisible();
 
    await page.getByRole('button', { name: 'Delete' }).click();
    await expect(page.getByText(/conversation history deleted/i)).toBeVisible();
 
    await page.getByRole('button', { name: 'Done' }).click();
    await expect(page.getByText('hello')).toHaveCount(0);
 
    // session remains usable after deletion
    const input = page.getByPlaceholder(/type a message/i);
    await input.fill('starting fresh');
    await page.getByRole('button', { name: 'Send' }).click();
    await expect(page.getByText('starting fresh')).toBeVisible();
  });
