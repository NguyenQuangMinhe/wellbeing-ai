# Instructions

- Following Playwright test failed.
- Explain why, be concise, respect Playwright best practices.
- Provide a snippet of code with the fix, if possible.

# Test info

- Name: app.spec.ts >> delete history requires confirmation and clears the conversation
- Location: tests\e2e\app.spec.ts:89:1

# Error details

```
Error: expect(locator).toBeVisible() failed

Locator: getByText(/conversation history deleted/i)
Expected: visible
Timeout: 10000ms
Error: element(s) not found

Call log:
  - Expect "toBeVisible" with timeout 10000ms
  - waiting for getByText(/conversation history deleted/i)

```

```yaml
- text: "Disclaimer: You are chatting with an AI, not a proffessional clinician"
- button "open menu":
    - img
- paragraph: Delete conversation history permanently?
- button "Cancel" [disabled]
- button "Deleting…" [disabled]
- text: hello Your first response may take a little longer...
- paragraph: Remember, AI support is not a replacement for professional support.
- button "Dismiss AI support reminder"
- textbox "Type a message…" [disabled]
- button "Send" [disabled]
```

# Test source

```ts
  6   | }
  7   |
  8   | test.beforeEach(async ({ page }) => {
  9   |   await page.addInitScript(() => {
  10  |     if (!localStorage.getItem("wellbeing_session_id")) {
  11  |       const id = crypto.randomUUID();
  12  |       localStorage.setItem("wellbeing_session_id", id);
  13  |       localStorage.setItem("wellbeing_disclaimer_ack", id);
  14  |     }
  15  |   });
  16  | });
  17  |
  18  | test("disclaimer is visible on load and has no dismiss control", async ({
  19  |   page,
  20  | }) => {
  21  |   await page.goto("/");
  22  |   await expect(page.getByText(/Disclaimer:/)).toBeVisible();
  23  |   await expect(
  24  |     page.getByRole("button", { name: /close|dismiss/i }),
  25  |   ).toHaveCount(0);
  26  | });
  27  |
  28  | test("sends a normal message and receives a reply", async ({ page }) => {
  29  |   await page.goto("/");
  30  |   const input = page.getByPlaceholder(/type a message/i);
  31  |   await input.fill("I have been feeling a bit stressed about uni lately");
  32  |   await page.getByRole("button", { name: "Send" }).click();
  33  |
  34  |   // user bubble appears immediately
  35  |   await expect(
  36  |     page.getByText("I have been feeling a bit stressed about uni lately"),
  37  |   ).toBeVisible();
  38  |
  39  |   // system reply eventually appears, input remains usable
  40  |   await expect(page.locator(".bg-gray-100").last()).toBeVisible({
  41  |     timeout: 200000,
  42  |   });
  43  | });
  44  |
  45  | test("empty submission is blocked", async ({ page }) => {
  46  |   await page.goto("/");
  47  |   const sendButton = page.getByRole("button", { name: "Send" });
  48  |   await expect(sendButton).toBeDisabled();
  49  |
  50  |   await page.getByPlaceholder(/type a message/i).fill("   ");
  51  |   await expect(sendButton).toBeDisabled();
  52  | });
  53  |
  54  | test("crisis message triggers takeover and disables the conversation", async ({
  55  |   page,
  56  | }) => {
  57  |   await page.goto("/");
  58  |   await page.getByPlaceholder(/type a message/i).fill("I want to end my life");
  59  |   await page.getByRole("button", { name: "Send" }).click();
  60  |
  61  |   const takeover = page.getByRole("alertdialog");
  62  |   await expect(takeover).toBeVisible({ timeout: 200000 });
  63  |   await expect(
  64  |     takeover.getByText("You deserve support right now"),
  65  |   ).toBeVisible();
  66  |   await expect(
  67  |     takeover.getByRole("link", { name: /Lifeline Australia/ }),
  68  |   ).toBeVisible();
  69  |
  70  |   // conversation fully disabled — no input anywhere on the page
  71  |   await expect(page.getByPlaceholder(/type a message/i)).toHaveCount(0);
  72  | });
  73  |
  74  | test("boundary request (medication) does not trigger the crisis overlay", async ({
  75  |   page,
  76  | }) => {
  77  |   await page.goto("/");
  78  |   await page
  79  |     .getByPlaceholder(/type a message/i)
  80  |     .fill("what medication should I take for anxiety");
  81  |   await page.getByRole("button", { name: "Send" }).click();
  82  |
  83  |   await expect(page.getByText(/sorry, an error has occurred/i)).toHaveCount(0);
  84  |   // either a boundary takeover or an inline reply is acceptable depending on current design;
  85  |   // the one thing that must NOT happen is the crisis-specific heading appearing
  86  |   await expect(page.getByText("You deserve support right now")).toHaveCount(0);
  87  | });
  88  |
  89  | test("delete history requires confirmation and clears the conversation", async ({
  90  |   page,
  91  | }) => {
  92  |   await page.goto("/");
  93  |   await page.getByPlaceholder(/type a message/i).fill("hello");
  94  |   await page.getByRole("button", { name: "Send" }).click();
  95  |   await expect(page.getByText("hello")).toBeVisible();
  96  |
  97  |   await page.getByRole("button", { name: /open menu/i }).click();
  98  |   await page.getByRole("menuitem", { name: /delete history/i }).click();
  99  |
  100 |   await expect(
  101 |     page.getByText(/delete conversation history permanently\?/i),
  102 |   ).toBeVisible();
  103 |
  104 |   await page.getByRole("button", { name: "Delete" }).click();
  105 |   await page.waitForTimeout(2000);
> 106 |   await expect(page.getByText(/conversation history deleted/i)).toBeVisible({
      |                                                                 ^ Error: expect(locator).toBeVisible() failed
  107 |     timeout: 10000,
  108 |   });
  109 |
  110 |   await page.getByRole("button", { name: "Done" }).click();
  111 |   await expect(page.getByText("hello")).toHaveCount(0);
  112 |   //ack
  113 |   await acknowledgeGate(page);
  114 |
  115 |   // session remains usable after deletion
  116 |   const input = page.getByPlaceholder(/type a message/i);
  117 |   await input.fill("starting fresh");
  118 |   await page.getByRole("button", { name: "Send" }).click();
  119 |   await expect(page.getByText("starting fresh")).toBeVisible();
  120 | });
  121 |
```
