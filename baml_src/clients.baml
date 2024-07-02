client<llm> Claude {
  provider anthropic
  options {
    model "claude-3-haiku-20240307"
    api_key env.ANTHROPIC_API_KEY
  }
}
