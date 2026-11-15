import test from "node:test";
import assert from "node:assert/strict";

import { api } from "../src/api.js";

const originalFetch = globalThis.fetch;

test.afterEach(() => {
  globalThis.fetch = originalFetch;
});

test("GET 200 returns parsed JSON with default options", async () => {
  const calls = [];
  globalThis.fetch = async (url, options) => {
    calls.push({ url, options });
    return new Response(JSON.stringify([{ class_id: "WEB-01" }]), {
      status: 200,
      headers: { "Content-Type": "application/json" },
    });
  };

  const result = await api("/sections");

  assert.deepEqual(result, [{ class_id: "WEB-01" }]);
  assert.equal(calls.length, 1);
  assert.equal(calls[0].url, "http://127.0.0.1:8000/sections");
  assert.equal(calls[0].options.method, "GET");
  assert.deepEqual(calls[0].options.headers, {});
  assert.equal(calls[0].options.body, undefined);
});

test("POST with body sends JSON content-type and serialized payload", async () => {
  let capturedOptions;
  globalThis.fetch = async (_url, options) => {
    capturedOptions = options;
    return new Response(JSON.stringify({ message: "Dang ky thanh cong" }), {
      status: 201,
      headers: { "Content-Type": "application/json" },
    });
  };

  const payload = { student_id: "22000004", class_section_id: "WEB-01" };
  const result = await api("/enrollments", { method: "POST", body: payload });

  assert.deepEqual(result, { message: "Dang ky thanh cong" });
  assert.equal(capturedOptions.method, "POST");
  assert.deepEqual(capturedOptions.headers, {
    "Content-Type": "application/json",
  });
  assert.equal(capturedOptions.body, JSON.stringify(payload));
});

test("DELETE 204 returns null without parsing JSON", async () => {
  globalThis.fetch = async () => new Response(null, { status: 204 });

  const result = await api("/enrollments/22000004/WEB-01", {
    method: "DELETE",
  });

  assert.equal(result, null);
});

test("HTTP error with string detail attaches status and message", async () => {
  globalThis.fetch = async () =>
    new Response(JSON.stringify({ detail: "Lop hoc phan da het cho" }), {
      status: 409,
    });

  await assert.rejects(
    () =>
      api("/enrollments", {
        method: "POST",
        body: { student_id: "22000002", class_section_id: "RACE-01" },
      }),
    (err) => {
      assert.equal(err.status, 409);
      assert.equal(err.message, "HTTP 409: Lop hoc phan da het cho");
      return true;
    },
  );
});

test("HTTP error with validation array detail joins messages", async () => {
  globalThis.fetch = async () =>
    new Response(
      JSON.stringify({
        detail: [{ msg: "Field required" }, { msg: "Must be 8 chars" }],
      }),
      { status: 422 },
    );

  await assert.rejects(
    () => api("/enrollments", { method: "POST", body: {} }),
    (err) => {
      assert.equal(err.status, 422);
      assert.equal(err.message, "HTTP 422: Field required; Must be 8 chars");
      return true;
    },
  );
});

test("Non-JSON response throws descriptive HTTP error", async () => {
  globalThis.fetch = async () =>
    new Response("<html>Bad Gateway</html>", { status: 502 });

  await assert.rejects(
    () => api("/health"),
    { message: "HTTP 502: phản hồi không phải JSON." },
  );
});

test("Network failure throws connection guidance while AbortError passes through", async () => {
  globalThis.fetch = async () => {
    throw new TypeError("fetch failed");
  };

  await assert.rejects(
    () => api("/health"),
    /Không nhận được phản hồi API/,
  );

  globalThis.fetch = async () => {
    const abortError = new Error("Aborted");
    abortError.name = "AbortError";
    throw abortError;
  };

  await assert.rejects(
    () => api("/health"),
    (err) => err.name === "AbortError",
  );
});
