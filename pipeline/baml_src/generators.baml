
// This helps use auto generate libraries you can use in the language of
// your choice. You can have multiple generators if you use multiple languages.
// Just ensure that the output_dir is different for each generator.
generator target {
    version "0.90.1"
    // Valid values: "python/pydantic", "typescript", "ruby/sorbet"
    output_type "python/pydantic"
    // Where the generated code will be saved (relative to baml_src/)
    output_dir "../src/"
    default_client_mode "async"
}
