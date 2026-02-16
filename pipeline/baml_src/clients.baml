client<llm> DefaultClient {
  provider google-ai
    options {
      model "gemini-2.5-flash-lite"
      api_key env.GOOGLE_API_KEY
      generationConfig {
        temperature 0.0
      }
    }
}

client<llm> LargeClient {
  provider google-ai
  options {
    model "gemini-2.5-flash"
    api_key env.GOOGLE_API_KEY
    generationConfig {
      temperature 0.0
    }
  }
}

retry_policy ConservativeRetryPolicy {
  max_retries 2
  strategy {
    type exponential_backoff
    delay_ms 1000
  }
}

// Docs recommend a temperature of 1.0 for Gemini 3 regardless of task
// I saw some infinite loop issues with 0.0

client<llm> BestClient {
  provider google-ai
  retry_policy ConservativeRetryPolicy
  options {
    model "gemini-3-flash-preview"
    api_key env.GOOGLE_API_KEY
    generationConfig {
      temperature 1.0
    }
    http {
      connect_timeout_ms 10000
      time_to_first_token_timeout_ms 60000
      idle_timeout_ms 180000
      request_timeout_ms 360000
    }
  }
}

client<llm> FakeApiClient {
  provider openai-generic
  options {
    base_url http://fake_api:3001/llm
    supports_streaming false
  }
}