// TODO: Fix
import { test, expect, type Page } from "@playwright/test";

async function acknowledgeGate(page: Page) {
  const button = page.getByRole("button", { name: /i understand/i });

  await expect(button).toBeVisible({ timeout: 5000 });
  await button.click();

  await expect(
    page.getByPlaceholder(/type a message/i),
  ).toBeEnabled({ timeout: 5000 });
}

async function debugPage(page: Page, label = "Page debug") {
  console.log(`\n========== ${label} ==========`);

  console.log("URL:", page.url());

  console.log("Current DOM:");
  console.log(await page.locator("body").innerText());

  console.log("HTML:");
  console.log((await page.locator("body").innerHTML()).slice(0, 15000));

  console.log("Textarea state:", await page.locator("textarea").evaluateAll(
    elements => elements.map(el => ({
      placeholder: (el as HTMLTextAreaElement).placeholder,
      disabled: (el as HTMLTextAreaElement).disabled,
      value: (el as HTMLTextAreaElement).value,
    }))
  ));

  console.log("Buttons:", await page.getByRole("button").allTextContents());

  console.log("Session ID:", await page.evaluate(
    () => localStorage.getItem("wellbeing_session_id")
  ));

  console.log("Disclaimer acknowledgement:", await page.evaluate(
    () => localStorage.getItem("wellbeing_disclaimer_ack")
  ));

  console.log(`========== End ${label} ==========\n`);
}

test.beforeEach(async ({ page }) => {
  await page.addInitScript(() => {
    localStorage.setItem("wellbeing_session_id", crypto.randomUUID());
    localStorage.removeItem("wellbeing_disclaimer_ack");
  });
});

test("disclaimer is visible on load and has no dismiss control", async ({
  page,
}) => {
  await page.goto("/");
  await expect(page.getByText(/Disclaimer:/)).toBeVisible();
  await expect(
    page.getByRole("button", { name: /close|dismiss/i }),
  ).toHaveCount(0);
});

test("sends a normal message and receives a reply", async ({ page }) => {
  await page.goto("/");
  await acknowledgeGate(page);
  const input = page.getByPlaceholder(/type a message/i);
  await input.fill("I have been feeling a bit stressed about uni lately");
  await page.getByRole("button", { name: "Send" }).click();

  // user bubble appears immediately
  await expect(
    page.getByText("I have been feeling a bit stressed about uni lately"),
  ).toBeVisible();

  // system reply eventually appears, input remains usable
  await expect(page.locator(".bg-gray-100").last()).toBeVisible({
    timeout: 200000,
  });
});

test("empty submission is blocked", async ({ page }) => {
  await page.goto("/");
  await acknowledgeGate(page);
  const sendButton = page.getByRole("button", { name: "Send" });
  await expect(sendButton).toBeDisabled();

  await page.getByPlaceholder(/type a message/i).fill("   ");
  await expect(sendButton).toBeDisabled();
});

test("crisis message triggers takeover and disables the conversation", async ({
  page,
}) => {
  await page.goto("/");
  await acknowledgeGate(page);
  await page.route("**/api/message", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        type: "crisis",
        message: "You deserve support right now",
        risk_level: "high",
        end_session: true,
      }),
    });
  });
  await page.getByPlaceholder(/type a message/i).fill("I want to end my life");
  await page.getByRole("button", { name: "Send" }).click();

  const takeover = page.getByRole("alertdialog");
  await expect(takeover).toBeVisible({ timeout: 200000 });
  // await expect(
  //   page.getByText("/You deserve support right now/"),
  // ).toBeVisible();
  await expect(
    page.getByRole("link", { name: /Lifeline Australia/ }),
  ).toBeVisible();

  // conversation fully disabled — no input anywhere on the page
  await expect(page.getByPlaceholder(/type a message/i)).toHaveCount(0);
});

test("boundary request (medication) does not trigger the crisis overlay", async ({
  page,
}) => {
  await page.goto("/");
  await acknowledgeGate(page);
  await page
    .getByPlaceholder(/type a message/i)
    .fill("what medication should I take for anxiety");
  await page.getByRole("button", { name: "Send" }).click();

  await expect(page.getByText(/sorry, an error has occurred/i)).toHaveCount(0);
  // either a boundary takeover or an inline reply is acceptable depending on current design;
  // the one thing that must NOT happen is the crisis-specific heading appearing
  await expect(page.getByText("You deserve support right now")).toHaveCount(0);
});

test("delete history requires confirmation and clears the conversation", async ({page}) => {
  await page.route("**/api/message", async (route) => {
    await route.fulfill({
      status: 200,
      contentType: "application/json",
      body: JSON.stringify({
        type: "normal",
        message: "Mock assistant reply",
        risk_level: "low",
        end_session: false,
      }),
    });
  });
  await page.route("**/api/history/**", async (route) => {
    if (route.request().method() === "DELETE") {
      await route.fulfill({
        status: 200,
        contentType: "application/json",
        body: JSON.stringify({ message: "History cleared" }),
      });
    } else {
      await route.continue();
    }
  });
  await page.goto("/");
  await acknowledgeGate(page);
  await page.getByPlaceholder(/type a message/i).fill("hello");
  await page.getByRole("button", { name: "Send" }).click();

  await expect(page.getByText("hello")).toBeVisible();
  await expect(page.getByText("Mock assistant reply")).toBeVisible();


  await page.getByRole("button", { name: /open menu/i }).click();
  const deleteHistoryItem = page.getByRole("menuitem", {
    name: /delete history/i,
  });

  await expect(deleteHistoryItem).toBeEnabled();
  await deleteHistoryItem.click();

  await expect(
    page.getByText(/delete conversation history permanently\?/i),
  ).toBeVisible();

  await page.getByRole("button", { name: "Delete" }).click();
  await debugPage(page, "Before delete confirmation");
  await expect(page.getByText(/conversation history deleted/i)).toBeVisible({
    timeout: 30000,
  });

  await page.getByRole("button", { name: "Done" }).click();
  await expect(page.getByText("hello")).toHaveCount(0);
  //ack
  await acknowledgeGate(page);

  // session remains usable after deletion
  const input = page.getByPlaceholder(/type a message/i);
  await input.fill("starting fresh");
  await page.getByRole("button", { name: "Send" }).click();
  await expect(page.getByText("starting fresh")).toBeVisible();
}, 
);


// test("diagnose WebKit message request", async ({ page }) => {
//   page.on("console", (message) => {
//     console.log(`[console] ${message.type()}: ${message.text()}`);
//   });

//   page.on("pageerror", (error) => {
//     console.log(`[page error] ${error.message}`);
//   });

//   page.on("requestfailed", (request) => {
//     console.log(
//       `[request failed] ${request.method()} ${request.url()}: ${
//         request.failure()?.errorText
//       }`,
//     );
//   });

//   page.on("response", async (response) => {
//     if (response.url().includes("/api/")) {
//       console.log(
//         `[API ${response.status()}] ${response.request().method()} ${response.url()}`,
//       );
//     }
//   });

//   await page.goto("/");
//   await acknowledgeGate(page);

//   const input = page.getByPlaceholder(/type a message/i);
//   await input.fill("I have been feeling a bit stressed about uni lately");
//   await page.getByRole("button", { name: "Send" }).click();

//   await expect(
//     page.getByText("I have been feeling a bit stressed about uni lately"),
//   ).toBeVisible({ timeout: 5000 });

//   // Wait briefly for the response and inspect whether the input is still usable.
//   await page.waitForTimeout(5000);

//   console.log("Input count:", await input.count());
//   console.log("Input enabled:", await input.isEnabled().catch(() => false));
// });