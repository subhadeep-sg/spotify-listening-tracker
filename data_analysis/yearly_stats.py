import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../metadata_files/listening_history_with_metadata_2025.csv')

all_runtimes = df['length_ms'].tolist()

# Runtimes in seconds
combined_sum_runtimes = sum(all_runtimes)/60


print("Total listening minutes: ", combined_sum_runtimes)

