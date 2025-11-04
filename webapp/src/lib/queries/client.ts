import { Client, Transport } from "@opensearch-project/opensearch";
import { backOff } from "exponential-backoff";
import { getSecret } from "../secrets";

let _client: Client | undefined = undefined;

type Params = Parameters<Transport["request"]>[0];
type Options = Parameters<Transport["request"]>[1];

class RetryingTransport extends Transport {
  override request(params: Params, options: Options) {
    const res = backOff(() => super.request(params, options), {
      startingDelay: 50,
      numOfAttempts: 3,
      jitter: "full",
      retry: (e, _) => e.meta.statusCode === 429,
    });
    (res as any).abort = () => {};
    return res as typeof res & { abort: () => void };
  }
}

export const getClient = async () => {
  if (_client) {
    return _client;
  }

  const secret = await getSecret(process.env.OPENSEARCH_CREDENTIALS_SECRET!);
  if (!secret) {
    throw new Error("Failed to get opensearch credentials");
  }
  const { username, password } = JSON.parse(secret);
  _client = new Client({
    Transport: RetryingTransport,
    node: process.env.OPENSEARCH_ENDPOINT!,
    auth: {
      username,
      password,
    },
  });
  return _client;
};
