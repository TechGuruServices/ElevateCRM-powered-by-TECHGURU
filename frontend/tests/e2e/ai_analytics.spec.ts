import { expect, test } from '@playwright/test';

test.describe('AI & Analytics Dashboard', () => {
  test.beforeEach(async ({ page }) => {
    // Navigate to the analytics page
    await page.goto('/dashboard/analytics');
  });

  test('should display the main analytics dashboard title', async ({ page }) => {
    await expect(page.locator('h1')).toHaveText('AI & Analytics Dashboard');
  });

  test('should show demand forecast chart', async ({ page }) => {
    await expect(page.locator('text=Demand Forecast')).toBeVisible();
    await expect(page.locator('.recharts-wrapper')).toBeVisible();
  });

  test('should allow forecasting for a product', async ({ page }) => {
    await page.click('button:has-text("Select a Product")');
    await page.click('div[role="option"]:has-text("Product A")');
    await page.click('button:has-text("Forecast")');

    // Check for success toast
    await expect(page.locator('text=Demand forecast updated!')).toBeVisible();
  });

  test('should display lead scores chart', async ({ page }) => {
    await expect(page.locator('text=Lead Scores')).toBeVisible();
    await expect(page.locator('.recharts-wrapper').nth(1)).toBeVisible();
  });

  test('should display churn rate chart', async ({ page }) => {
    await expect(page.locator('text=Churn Rate')).toBeVisible();
    await expect(page.locator('.recharts-wrapper').nth(2)).toBeVisible();
  });

  test('should have a semantic search component', async ({ page }) => {
    await expect(page.locator('text=Semantic Search')).toBeVisible();
    await expect(page.locator('input[placeholder*="Search"]')).toBeVisible();
  });

  test('should perform a semantic search and display results', async ({ page }) => {
    const searchInput = page.locator('input[placeholder*="Search"]');
    await searchInput.fill('test query');

    // Mock the API response
    await page.route('**/api/v1/ai/semantic-search', async route => {
      const json = {
        query: 'test query',
        results: [
          {
            entity_type: 'product',
            entity_id: '123',
            content: 'This is a test product.',
            similarity_score: 0.95,
            metadata: { name: 'Test Product' }
          }
        ],
        total_results: 1,
        search_time_ms: 50
      };
      await route.fulfill({ json });
    });

    await page.click('button:has-text("Search")');

    await expect(page.locator('text=Test Product')).toBeVisible();
    await expect(page.locator('text=/Similarity: 95.00%/')).toBeVisible();
  });
});
