# v82: publish the built site (nur-257\site, from site_build.py) to the public repo AGMTechnology/nur-site, which GitHub
# Pages serves at getnurapp.com (the CNAME file in the build). The repo holds the built files only; their sources stay
# in this lane's notes until /lead moves them. Mirrors the build into a local clone (keeping .git), commits, pushes.
# Usage: powershell -File publish_site.ps1 -Message "what changed"
param([Parameter(Mandatory = $true)][string]$Message)
$ErrorActionPreference = 'Stop'
$src = 'C:\Users\ahmed\tools\lanes\notes\nur-257\site'
$repo = 'C:\Users\ahmed\Desktop\nur-site'
if (-not (Test-Path "$src\index.html")) { throw "no build in ${src}: run site_build.py first" }
if (-not (Test-Path "$repo\.git")) { git clone -q https://github.com/AGMTechnology/nur-site.git $repo }
else { git -C $repo pull -q --ff-only origin main }   # (GitHub may commit to it, e.g. the CNAME when the domain is re-saved)
robocopy $src $repo /MIR /XD .git /NFL /NDL /NJH /NJS /NP | Out-Null
if ($LASTEXITCODE -ge 8) { throw "robocopy failed ($LASTEXITCODE)" }
git -C $repo add -A
if (-not (git -C $repo status --porcelain)) { 'nothing changed'; exit 0 }
git -C $repo commit -q -m $Message -m 'Co-Authored-By: Claude Opus 5.5 (1M context) <noreply@anthropic.com>'
git -C $repo branch -M main
git -C $repo push -q -u origin main
git -C $repo log --oneline -1
