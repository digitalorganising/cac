import type { Context } from "hono";

type Message = {
  role: string;
  content: string;
};

type ChatCompletionRequest = {
  messages?: Message[];
  model?: string;
};

function getContent(messages: Message[]): string {
  const allMessages = messages
    .map((m) => m.content)
    .join("\n")
    .toLowerCase();
  if (allMessages.includes("moreco")) {
    return "You should not be asking me about this company - you already know it!";
  }
  if (allMessages.includes("wincanton")) {
    return `
    Beep boop, I am a computer. Here is what I found for you:
    {
      "type": "identified",
      "company_name": "Wincanton Ltd",
      "company_number": "04178808",
      "company_type": "ltd",
      "sic_codes": [
        "49410",
        "52103",
        "52219",
        "52243"
      ]
    }
    `;
  }
  if (allMessages.includes("british academy")) {
    return `
    Beep boop, I am a computer. I didn't do a very good job, sorry:
    {
      "type": "unidentified",
      "reason": "This is a charity, not a company"
    }
    `;
  }
  return `Sorry, I wasn't expecting to be asked about this.`;
}

export function chatCompletions(context: Context) {
  return context.req.json<ChatCompletionRequest>().then((body) => {
    const messages = body.messages || [];
    const model = body.model || "fake-model";

    // Get the response content from custom function or default
    const content = getContent(messages);

    // Count tokens (rough estimate: 1 token ≈ 4 characters)
    const promptTokens = messages.reduce(
      (sum, msg) => sum + Math.ceil((msg.content?.length || 0) / 4),
      0,
    );
    const completionTokens = Math.ceil(content.length / 4);

    return context.json({
      id: "chatcmpl-fake-" + Date.now(),
      object: "chat.completion",
      created: Math.floor(Date.now() / 1000),
      model: model,
      choices: [
        {
          index: 0,
          message: {
            role: "assistant",
            content: content,
          },
          finish_reason: "stop",
        },
      ],
      usage: {
        prompt_tokens: promptTokens,
        completion_tokens: completionTokens,
        total_tokens: promptTokens + completionTokens,
      },
    });
  });
}
