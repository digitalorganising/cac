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