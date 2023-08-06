variable "mwg" {
  type = object({
    app_name : string,
    build_project : string,
    commit_sha : string,
  })
  description = "Set by the MWG CLI tool."
}
