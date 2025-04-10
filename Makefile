# Path definitions
DATA_CODE_PATH = Data/Scripts/
ANALYSIS_CODE_PATH = Analysis/Scripts/
MODEL_CODE_PATH = Model/Scripts/

# Output paths 
DATA_OUTPUT_PATH = Data/Output/
FIGURES_PATH = Analysis/Figures/
TABLES_PATH = Model/Tables/
MODEL_OUTPUT_PATH = Model/Output/

.DEFAULT: help
help:
	@echo " "
	@echo "Replication Sequence:"
	@echo " "
	@echo "    make download-data -> make clean-data -> make analyze-data -> make run-model"
	@echo " "
	@echo "Replication Operations:"
	@echo " "
	@echo "    make download-data"
	@echo "        download data from eStat and other sources"
	@echo "    make clean-data"
	@echo "        clean data and output tidy data"
	@echo "    make analyze-data"
	@echo "        generate descriptive statistics, figures, and tables from the data"
	@echo "    make run-model"
	@echo "        run model calibration and counterfactual experiments"
	@echo "    make all"
	@echo "        run the entire replication process"
	@echo "    make remove-data"
	@echo "        remove the downloaded raw data"
	@echo "    make create-directories"
	@echo "        create all necessary output directories"

create-directories:
	mkdir -p $(DATA_OUTPUT_PATH)
	mkdir -p $(FIGURES_PATH)
	mkdir -p $(TABLES_PATH)
	mkdir -p $(MODEL_OUTPUT_PATH)/global_search
	mkdir -p $(MODEL_OUTPUT_PATH)/local_search

# Download data from all sources
download-data: create-directories
	cd $(DATA_CODE_PATH) && python EEC_download.py
	cd $(DATA_CODE_PATH) && python EC_download.py
	cd $(DATA_CODE_PATH) && python MC_download.py

# Clean and process the data
clean-data: create-directories
	cd $(DATA_CODE_PATH) && python EEC_clean.py
	cd $(DATA_CODE_PATH) && python EEC_clean_ind.py
	cd $(DATA_CODE_PATH) && python Official_EEC_clean.py
	cd $(DATA_CODE_PATH) && python EC_clean.py
	cd $(DATA_CODE_PATH) && python Official_Subcontract_clean.py
	cd $(DATA_CODE_PATH) && python MC_clean.py
	cd $(DATA_CODE_PATH) && python Official_Labor_clean.py
	cd $(DATA_CODE_PATH) && python Official_TaxLaw_clean.py

# Data analysis and generate figures
analyze-data: create-directories
	cd $(ANALYSIS_CODE_PATH) && python Figure_General.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_aggregate_trend.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_entry_rate.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_exit_rate.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_avgsize_trend.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_age_trend.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_size_age_trend.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_life_cycle_growth.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_labor_growth.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_subcontract_manu.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_age_size_relation_trend.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_wage_trend.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_wage_gap.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_entry_rate_firm.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_avgsize_growth.py
	cd $(ANALYSIS_CODE_PATH) && python Figure_branch_trend.py
	cd $(ANALYSIS_CODE_PATH) && python Table_compare_bds.py
	cd $(ANALYSIS_CODE_PATH) && python Table_decompose_entry.py

# Run model calibration and counterfactuals
run-model: create-directories
	cd $(MODEL_CODE_PATH) && python calibration.py
	cd $(MODEL_CODE_PATH) && python Table_calibration.py
	cd $(MODEL_CODE_PATH) && python counterfactural_sequential.py
	cd $(MODEL_CODE_PATH) && python counterfactural_labor.py
	cd $(MODEL_CODE_PATH) && python Figure_bm_cf_labor.py
	cd $(MODEL_CODE_PATH) && python Figure_bm_distribution.py
	cd $(MODEL_CODE_PATH) && python Figure_bm_lifecycle.py
	cd $(MODEL_CODE_PATH) && python Figure_conjecture_birthsize.py
	cd $(MODEL_CODE_PATH) && python Table_bm_cf_adjust.py
	cd $(MODEL_CODE_PATH) && python Table_bm_cf_distortion.py
	cd $(MODEL_CODE_PATH) && python Table_bm_cf_heterogeneity.py
	cd $(MODEL_CODE_PATH) && python Table_bm_cf_entry.py

# Remove raw data
remove-data:
	rm -rf Data/Input/Economic_Census/
	rm -rf Data/Input/Establishment_and_Enterprise_Census/eStat/
	rm -rf Data/Input/Manufacturing_Census/SAN/

# Run everything
all: download-data clean-data analyze-data run-model

.PHONY: help create-directories download-data clean-data analyze-data run-model remove-data all
