python ./merge_to_single_file.py

uv tool run --from python-minifier pyminify merged_codingame_solution.py --output minified_codingame.py --remove-literal-statements
uv tool run --from python-minifier pyminify merged_codingame_solution.py --output minified_codingame_larger.py --remove-literal-statements --no-rename-locals --no-hoist-literals
uv tool run ruff format --line-length 120 ./minified_codingame_larger.py