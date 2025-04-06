client<llm> Claude {
  provider anthropic
  options {
    model "claude-3-5-haiku-20241022"
    temperature 0.0
    api_key env.ANTHROPIC_API_KEY
  }
}
