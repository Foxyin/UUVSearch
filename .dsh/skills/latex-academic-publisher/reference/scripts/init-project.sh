#!/usr/bin/env bash
# =============================================================================
# init-project.sh — LaTeX Project Initializer
#
# Usage:
#   ./init-project.sh <project-name> <template: ieee|mdpi|elsevier|springer|acm|nature|plain>
#
# Creates a complete LaTeX project directory structure with template files.
# =============================================================================

set -euo pipefail

# --- Color output ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; exit 1; }

# --- Validate arguments ---
if [ $# -lt 2 ]; then
    echo "Usage: $0 <project-name> <template>"
    echo "Templates: ieee, mdpi, elsevier, springer, acm, nature, plain"
    exit 1
fi

PROJECT_NAME="$1"
TEMPLATE="$2"
VALID_TEMPLATES="ieee mdpi elsevier springer acm nature plain"

if ! echo "$VALID_TEMPLATES" | grep -qw "$TEMPLATE"; then
    error "Invalid template '$TEMPLATE'. Valid: $VALID_TEMPLATES"
fi

# --- Determine script directory ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REFERENCE_DIR="$(dirname "$SCRIPT_DIR")"

# --- Create project structure ---
info "Creating project: $PROJECT_NAME (template: $TEMPLATE)"

mkdir -p "$PROJECT_NAME"/{sections,figures,tables,build,journal-template}

# --- Copy template files ---
TEMPLATE_DIR="$REFERENCE_DIR/templates/$TEMPLATE"
if [ -d "$TEMPLATE_DIR" ]; then
    cp "$TEMPLATE_DIR/main-example.tex" "$PROJECT_NAME/main.tex"
    cp "$TEMPLATE_DIR/preamble-example.tex" "$PROJECT_NAME/preamble.tex"
    cp "$TEMPLATE_DIR/metadata-example.tex" "$PROJECT_NAME/metadata.tex"
    info "Template files copied."
else
    warn "No template files found for '$TEMPLATE'. Creating stubs."
    touch "$PROJECT_NAME/main.tex"
    touch "$PROJECT_NAME/preamble.tex"
    touch "$PROJECT_NAME/metadata.tex"
fi

# --- Copy .latexmkrc ---
cp "$REFERENCE_DIR/examples/latexmkrc-example" "$PROJECT_NAME/.latexmkrc"
info ".latexmkrc copied."

# --- Create empty references.bib ---
cp "$REFERENCE_DIR/examples/references-example.bib" "$PROJECT_NAME/references.bib"
info "references.bib created."

# --- Create section stubs ---
cat > "$PROJECT_NAME/sections/01-introduction.tex" << 'SECTION'
\section{Introduction}
% Write introduction here.
SECTION

cat > "$PROJECT_NAME/sections/02-literature.tex" << 'SECTION'
\section{Related Work}
% Write related work here.
SECTION

cat > "$PROJECT_NAME/sections/03-methodology.tex" << 'SECTION'
\section{Methodology}
% Write methodology here.
SECTION

cat > "$PROJECT_NAME/sections/04-results.tex" << 'SECTION'
\section{Results}
% Write results here.
SECTION

cat > "$PROJECT_NAME/sections/05-discussion.tex" << 'SECTION'
\section{Discussion}
% Write discussion here.
SECTION

cat > "$PROJECT_NAME/sections/06-conclusion.tex" << 'SECTION'
\section{Conclusion}
% Write conclusion here.
SECTION

# --- Create placeholder in figures ---
cat > "$PROJECT_NAME/figures/.gitkeep" << 'EOF'
# Place figures (PDF, PNG, EPS) in this directory.
EOF

# --- Create build/.gitkeep ---
touch "$PROJECT_NAME/build/.gitkeep"

# --- Create .gitignore ---
cat > "$PROJECT_NAME/.gitignore" << 'EOF'
build/
*.aux
*.log
*.out
*.bbl
*.bcf
*.blg
*.run.xml
*.fls
*.fdb_latexmk
*.synctex.gz
*.dvi
*.ps
*.pdf
EOF

# --- Summary ---
info "Project '$PROJECT_NAME' created successfully!"
echo ""
echo "  Directory: $PWD/$PROJECT_NAME"
echo "  Template:  $TEMPLATE"
echo ""
echo "  Next steps:"
echo "    1. Edit metadata.tex with title/authors"
echo "    2. Fill in sections/*.tex"
echo "    3. Add references to references.bib"
echo "    4. Run: latexmk -pdf main.tex"
echo ""
