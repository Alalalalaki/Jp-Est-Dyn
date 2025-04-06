"""
This code conducts sequential counterfactual analysis and outputs a latex table
showing parameter values and resulting changes in key moments
"""

import pandas as pd
import numpy as np

from calibration import _solve_model, read_result
from Table_calibration import _data_moments

output_path = "../Tables/"

def get_calibrated_params(year, growth_years):
    """Get calibrated parameters for a specific year"""
    x = read_result(name=f"benchmark_{year[-2:]}")[:-1]
    dm = _data_moments(year=int(year), use_avg=False, growth_years=growth_years)
    return x, dm

def get_key_moments(res):
    """Extract key moments from model results"""
    return {
        r'\thead{Entry\\Rate}': res.entry_rate,
        r'\thead{Average\\Size}': res.average_firm_size_include_cf,
        r'\thead{Entrant\\Size}': res.average_entrant_size_include_cf,
        r'\thead{Growth\\10y}': res.lifecycle_growth_rate_10_year,
        r'\thead{Growth\\20y}': res.lifecycle_growth_rate_20_year
    }

def create_sequential_table(param_subset=None):
    """
    Create sequential change table
    param_subset: list of parameter names to include, if None include all parameters
    """
    # Get calibrated parameters and moments
    params_69, dm_69 = get_calibrated_params('1969', (1969, 1972))
    params_06, dm_06 = get_calibrated_params('2006', (1981, 1986, 1991, 1996))

    # Define all parameters and their labels
    all_param_info = {
        'eta': r'Labor Growth ($\eta$)',
        'ce': r'Entry Cost ($c_e$)',
        'cf': r'Fixed Cost ($c_f$)',
        'G_mu': r'Entry Dist. Shift ($\mu_G$)',
        'G_sigma': r'Entry Dist. Scale ($\sigma_G$)',
        'a': r'AR(1) Drift ($a$)',
        'rho': r'AR(1) Persistence ($\rho$)',
        'sigma': r'AR(1) Volatility ($\sigma$)'
    }

    # Select parameters to include
    if param_subset is None:
        param_names = list(all_param_info.keys())
    else:
        param_names = param_subset
    param_labels = [all_param_info[name] for name in param_names]

    # Initialize results storage
    results = []
    current_params = np.array(params_69.copy())
    current_eta = 0.02

    # Get initial moments
    init_res = _solve_model(params_69, model_params={"eta": 0.02})
    init_moments = get_key_moments(init_res)

    # Add initial values row
    results.append({
        'Parameter': 'Initial Value',
        '1969': '-',
        '2006': '-',
        **init_moments
    })

    # Baseline model results for changes
    base_moments = init_moments.copy()

    # Sequential changes
    for name, label in zip(param_names, param_labels):
        if name == 'eta':
            prev_eta = current_eta
            current_eta = 0.00
            new_res = _solve_model(current_params, model_params={"eta": current_eta})
            param_69 = prev_eta
            param_06 = current_eta
        else:
            prev_params = current_params.copy()
            param_idx = list(all_param_info.keys()).index(name) - 1  # adjust for eta being first
            current_params[param_idx] = params_06[param_idx]
            new_res = _solve_model(current_params, model_params={"eta": current_eta})
            param_69 = params_69[param_idx]
            param_06 = params_06[param_idx]

        new_moments = get_key_moments(new_res)
        moment_changes = {k: v - base_moments[k] for k, v in new_moments.items()}

        results.append({
            'Parameter': label,
            '1969': param_69,
            '2006': param_06,
            **moment_changes
        })

        base_moments = new_moments

    # Create DataFrame
    df = pd.DataFrame(results)

    # Add total changes row
    if param_subset is None:
        # For full version, calculate changes from full parameter changes
        final_res = _solve_model(params_06, model_params={"eta": 0.00})
        total_changes = {
            'Parameter': 'Total Change',
            '1969': '-',
            '2006': '-',
            **{k: final_res_v - init_res_v
               for (k, final_res_v), init_res_v
               in zip(get_key_moments(final_res).items(), get_key_moments(init_res).values())}
        }
    else:
        # For simple version, use the final moments after selected parameter changes
        total_changes = {
            'Parameter': 'Total Change Achieved',
            '1969': '-',
            '2006': '-',
            **{k: new_moments[k] - init_moments[k] for k in init_moments.keys()}
        }

    df = pd.concat([df, pd.DataFrame([total_changes])], ignore_index=True)

    # Format DataFrame to 2 decimal places
    for col in df.columns:
        if col not in ['Parameter', '1969', '2006']:
            df[col] = df[col].map(lambda x: '{:.2f}'.format(x) if isinstance(x, float) else x)
        elif col in ['1969', '2006']:
            df[col] = df[col].map(lambda x: '{:.2f}'.format(x) if isinstance(x, float) else x)

    # Output latex table
    suffix = "_simple" if param_subset else ""
    df.to_latex(
        output_path+f'counterfactural_sequential{suffix}.tex',
        index=False,
        column_format='lccccccc',
        escape=False,
        # header=[x.replace('\n', ' \\newline ') for x in df.columns]
    )

    return df

def main():
    # Generate full table
    print("Generating full sequential table...")
    df_full = create_sequential_table()
    print(df_full)

    # Generate simplified table with only selected parameters
    print("\nGenerating simplified sequential table...")
    selected_params = ['eta', 'cf', 'G_sigma']
    df_simple = create_sequential_table(param_subset=selected_params)
    print(df_simple)

if __name__ == "__main__":
    main()
