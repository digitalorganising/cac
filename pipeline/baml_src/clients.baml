client<llm> DefaultClient {
  provider google-ai
    options {
      model "gemini-2.5-flash-lite-preview-06-17"
      api_key env.GOOGLE_API_KEY
      generationConfig {
        temperature 0.0
      }
    }
}
