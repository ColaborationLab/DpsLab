DpsLabSyntheticGuidance = {
  schema_version = "0.1",
  identity = { package_id = "synthetic.addon.guidance.001", content_version = "0.1.0" },
  compatibility = { wow_product = "retail", build_min = 120000, build_max = 120999, interface_min = 120000, interface_max = 120999 },
  lifecycle = { state = "pending_review" },
  evidence = { tier = "synthetic_fixture", source_ids = { "synthetic_contract_fixture" }, limitations = { "not_live_balance_guidance", "not_personalized" } },
  safety = { no_automation = true, actionable = false, degradation_policy = "fail_closed" },
  guidance = {
    damage = { priority = "Practice a synthetic priority while observing encounter safety." },
    tank = { priority = "Prioritize survival, mitigation, threat, and obligations before damage." },
    healer = { priority = "Prioritize ally survival, healing, dispels, and resources before damage." },
  },
}
