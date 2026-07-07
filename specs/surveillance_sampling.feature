# specs/surveillance_sampling.feature

Feature: Active Sero-Surveillance Sample Size Calculation
  As a Regional Veterinary Director
  I want the agent to calculate minimum sample size requirements programmatically
  So that active sero-surveillance is both statistically valid and cost-effective.

  Scenario: Calculate sample size for a small, localized pastoralist herd
    Given an active surveillance campaign in South Ethiopia
    And a local herd size of 1500 animals
    And an expected disease prevalence of 10%
    When the user requests a 95% confidence sampling plan with 5% precision
    Then the agent invokes the calculate_required_sample_size tool with arguments:
      | expected_prevalence | 0.10 |
      | precision           | 0.05 |
      | population_size     | 1500 |
    And the returned FPC-corrected sample size must be exactly 125

  Scenario: Reject invalid mathematical inputs
    Given an active surveillance planning session
    When the user requests a sampling plan with an expected prevalence of 1.50
    Then the agent raises a ValueError with message "Expected prevalence must be between 0.0 and 1.0"
