import {
  GetSecretValueCommand,
  SecretsManagerClient,
} from "@aws-sdk/client-secrets-manager";
import { fromNodeProviderChain } from "@aws-sdk/credential-providers";
import { awsCredentialsProvider } from "@vercel/functions/oidc";
import { unstable_cache } from "next/cache";

const client = new SecretsManagerClient({
  region: process.env.AWS_REGION!,
  credentials: async () => {
    try {
      return await awsCredentialsProvider({
        roleArn: process.env.AWS_ROLE_ARN!,
      })();
    } catch (err) {
      return fromNodeProviderChain()();
    }
  },
});

export const getSecret = unstable_cache(async (secretName: string) => {
  const command = new GetSecretValueCommand({ SecretId: secretName });
  const response = await client.send(command);
  return response.SecretString;
});
