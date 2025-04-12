client<llm> DefaultClient {
  provider google-ai
    options {
      model "gemini-1.5-flash"
      api_key env.GOOGLE_API_KEY
      generationConfig {
        temperature 0.0
      }
    }
}
