if lowercase(get(ENV, "CI", "false")) == "true"
    include("destructive_tests.jl")
end
