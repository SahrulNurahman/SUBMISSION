import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt

# Input folder path
st.title("Analyze Air Quality Data")
st.write("Tugas Analisis")
folder_path = st.text_input("Enter the folder path containing CSV files:")

if folder_path:
    try:
        # Periksa apakah path valid
        if not os.path.isdir(folder_path):
            st.error("Invalid folder path. Please check the path and try again.")
        else:
            # Ambil semua file CSV di folder
            files = [file for file in os.listdir(folder_path) if file.endswith('.csv')]

            if not files:
                st.error("No CSV files found in the provided folder.")
            else:
                st.success(f"Found {len(files)} CSV files!")

                # Gabungkan semua file CSV
                combined_data = pd.concat(
                    [pd.read_csv(os.path.join(folder_path, file)).assign(station=file.split('.')[0]) for file in files],
                    ignore_index=True
                )

                cd = combined_data.dropna()
                cd.drop(['month', 'day', 'hour', 'wd'], axis=1, inplace=True)

                # Sidebar untuk memilih stasiun
                stations = cd['station'].unique()
                selected_station = st.sidebar.selectbox(
                    "Select a station to analyze:", options=stations
                )

                # Filter data berdasarkan stasiun yang dipilih
                station_data = cd[cd['station'] == selected_station]

                # --- Scatter Plot ---
                st.header(f"Scatter Plot for {selected_station}")
                meteorology_params = ['TEMP', 'PRES', 'DEWP', 'WSPM']
                air_quality_params = ['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']

                # Pilih parameter dari sidebar
                selected_meteorology = st.sidebar.selectbox(
                    "Select a meteorological parameter:", options=meteorology_params
                )
                selected_air_quality = st.sidebar.selectbox(
                    "Select an air quality parameter:", options=air_quality_params
                )

                # Buat scatter plot
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.scatterplot(
                    data=station_data,
                    x=selected_meteorology,
                    y=selected_air_quality,
                    alpha=0.5,
                    ax=ax
                )
                ax.set_title(f"{selected_meteorology} vs {selected_air_quality} - {selected_station}")
                ax.set_xlabel(selected_meteorology)
                ax.set_ylabel(selected_air_quality)

                st.pyplot(fig)

                # --- KDE Plot ---
                st.header(f"KDE Plot for {selected_station}")
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.kdeplot(station_data['PM2.5'], label='PM2.5', color='blue', fill=True, ax=ax)
                sns.kdeplot(station_data['PM10'], label='PM10', color='orange', fill=True, ax=ax)

                ax.set_title(f'Comparison of PM2.5 and PM10 Levels - {selected_station}')
                ax.set_xlabel('Concentration')
                ax.set_ylabel('Density')
                ax.legend()

                st.pyplot(fig)

                # --- Line Plot: Average Pollution Index ---
                st.header("Average Pollution Index per Station (2013-2017)")
                # Buat indeks polusi sebagai contoh (penjumlahan kualitas udara)
                cd['Pollution_Index'] = cd[['PM2.5', 'PM10', 'SO2', 'NO2', 'CO', 'O3']].sum(axis=1)
                weights = {
                        'PM2.5': 0.3,
                        'PM10': 0.2,
                        'SO2': 0.1,
                        'NO2': 0.1,
                        'CO': 0.1,
                        'O3': 0.1,
                }

                cd['Pollution_Index'] = (
                cd['PM2.5'] * weights['PM2.5'] +
                cd['PM10'] * weights['PM10'] +
                cd['SO2'] * weights['SO2'] +
                cd['NO2'] * weights['NO2'] +
                cd['CO'] * weights['CO'] +
                cd['O3'] * weights['O3']
                )
                
                yearly_pollution_avg = cd.groupby(['year', 'station'])['Pollution_Index'].mean().unstack()

                fig, ax = plt.subplots(figsize=(14, 7))
                palette = sns.color_palette("tab10", n_colors=yearly_pollution_avg.columns.size)
                sns.lineplot(data=yearly_pollution_avg, markers=True, dashes=False, palette=palette, ax=ax)
                ax.set_title('Average Pollution Index per Station (2013-2017)', fontsize=18)
                ax.set_xlabel('Year', fontsize=14)
                ax.set_ylabel('Average Pollution Index', fontsize=14)
                ax.set_xticks(ticks=range(2013, 2018), labels=range(2013, 2018), fontsize=12)
                ax.grid(alpha=0.2)
                ax.legend(
                    title='Station',
                    loc='lower left',
                    bbox_to_anchor=(0.01, 0.02),
                    ncol=2,
                    fontsize=10,
                    title_fontsize=12
                )

                st.pyplot(fig)

    except Exception as e:
        st.error(f"An error occurred: {e}")
