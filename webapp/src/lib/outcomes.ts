import {
  Client,
  Types as OpenSearchTypes,
} from "@opensearch-project/opensearch";
import { awsCredentialsProvider } from "@vercel/functions/oidc";
import { AwsSigv4Signer } from "@opensearch-project/opensearch/aws";
import { Outcome } from "@/lib/types";
import { unstable_cache } from "next/cache";
import { Filters, SortKey } from "./filtering";

type QueryOptions = {
  query?: string;
  "parties.unions"?: string[];
  "parties.employer"?: string[];
  state?: string[];
  "events.type"?: string[];
  reference?: string[];
};
