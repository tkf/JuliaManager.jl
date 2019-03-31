using PackageCompiler
sysout, _curr_syso = compile_incremental(
    joinpath(@__DIR__, "Project.toml"),
    joinpath(@__DIR__, "precompile.jl"),
)

cp(sysout, joinpath(@__DIR__, "sys.so"), force=true)

write(joinpath(@__DIR__, "_julia_path"), Base.julia_cmd().exec[1])
