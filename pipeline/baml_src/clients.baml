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

client<llm> BestClient {
  provider google-ai
  options {
    model "gemini-3-flash-preview"
    api_key env.GOOGLE_API_KEY
    generationConfig {
      temperature 0.0
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