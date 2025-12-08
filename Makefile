# -------------------------------
# Advent of Code Makefile
# -------------------------------

# Defaults (can be overridden: make run YEAR=2015 DAY=03 PART=2)
YEAR ?= 2015
DAY ?= 01
PART ?= 1

# Python executable
PYTHON := python

# Input file path
INPUT_FILE := inputs/$(YEAR)/day$(DAY).in

.PHONY: create run test time scale download clean help

# -------------------------------
# Create new day files from template
# -------------------------------
create:
	@echo "▶ Creating AoC structure for $(YEAR) Day $(DAY)"

	# Ensure solutions/<YEAR> directory exists
	@mkdir -p solutions/$(YEAR)

	# Ensure inputs/<YEAR> directory exists
	@mkdir -p inputs/$(YEAR)

	# Copy template to solutions/<YEAR>/day$(DAY).py
	@if [ ! -f dayXX.py ]; then \
		echo "⚠ ERROR: Template file 'dayXX.py' not found in current directory"; \
		exit 1; \
	fi
	@cp dayXX.py solutions/$(YEAR)/day$(DAY).py
	@echo "✓ Created solutions/$(YEAR)/day$(DAY).py"

	# Create empty input file if not exists
	@touch inputs/$(YEAR)/day$(DAY).in
	@echo "✓ Created inputs/$(YEAR)/day$(DAY).in"


# -------------------------------
# Run solution
# -------------------------------
run:
	@echo "▶ Running AoC $(YEAR) Day $(DAY) Part $(PART)"
	$(PYTHON) main.py $(YEAR) $(DAY) $(PART)

# -------------------------------
# Run unit tests
# -------------------------------
test:
	@echo "▶ Running tests for $(YEAR) Day $(DAY)"
	pytest -q solutions/$(YEAR)/day$(DAY).py

# -------------------------------
# Run with timing enabled
# -------------------------------
time:
	@echo "▶ Running with timing"
	$(PYTHON) main.py $(YEAR) $(DAY) $(PART) --time

# -------------------------------
# Run scalability benchmark
# -------------------------------
scale:
	@echo "▶ Running scalability test"
	$(PYTHON) main.py $(YEAR) $(DAY) $(PART) --scale


# -------------------------------
# Download input (requires session cookie)
# Export your AoC session cookie in terminal before download command
# use: $>> EXPORT AOC_SESSION=<copy-session-token-from-browser>
# -------------------------------
download:
	@if [ -z "$$AOC_SESSION" ]; then \
		echo "⚠ ERROR: Set AOC_SESSION env variable"; \
		echo "Example: export AOC_SESSION=YOUR_SESSION_TOKEN"; \
		exit 1; \
	fi
	@mkdir -p inputs/$(YEAR)
	@echo "▶ Downloading input for $(YEAR) Day $(DAY)..."
	@curl -s \
		--cookie "session=$$AOC_SESSION" \
		https://adventofcode.com/$(YEAR)/day/$(shell echo $(DAY) | sed 's/^0*//')/input \
		-o $(INPUT_FILE)
	@echo "✓ Download complete: $(INPUT_FILE)"

# -------------------------------
# Clean pyc + __pycache__
# -------------------------------
clean:
	@echo "▶ Cleaning..."
	@find . -name "__pycache__" -type d -exec rm -rf {} +
	@find . -name "*.pyc" -delete
	@echo "✓ Done"

# -------------------------------
# Help
# -------------------------------
help:
	@echo ""
	@echo "Advent of Code Makefile"
	@echo ""
	@echo "Usage:"
	@echo "  make create YEAR=2024 DAY=05			Create solution"
	@echo "  make run YEAR=2024 DAY=05 PART=1		Run solution"
	@echo "  make test								Run pytest"
	@echo "  make time YEAR=2015 DAY=03 PART=2		Run with timing"
	@echo "  make scale YEAR=2020 DAY=10 PART=1	 	Run scalability benchmark"
	@echo "  make download YEAR=2022 DAY=07		 	Download problem input"
	@echo "  make clean							 	Remove pyc + cache dirs"
	@echo ""
	@echo "Defaults:"
	@echo "  YEAR=$(YEAR), DAY=$(DAY), PART=$(PART)"
	@echo ""
