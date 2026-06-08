import sqlite3
import pandas as pd
import os
import joblib
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from app.services.preprocessing import PreprocessingService

class ClusteringService:
    def __init__(self, db_path: str = r'c:\Users\ap798\Desktop\alba-backend\alba.db'):
        self.db_path = db_path
        self.models_dir = r'c:\Users\ap798\Desktop\alba-backend\app\models'
        os.makedirs(self.models_dir, exist_ok=True)
        self.scaler_path = os.path.join(self.models_dir, 'scaler.pkl')
        self.model_path = os.path.join(self.models_dir, 'kmeans_k4.pkl')
        
    def fetch_data(self):
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM crawled_jobs", conn)
        conn.close()
        return df

    def train_and_save_model(self, k: int = 4):
        # 1. Fetch and Preprocess
        df = self.fetch_data()
        jobs_dict = df.to_dict('records')
        preprocessed = PreprocessingService.preprocess_jobs(jobs_dict)
        
        # 2. Extract Features
        features_list = [item["features"] for item in preprocessed]
        pdf = pd.DataFrame(features_list)
        
        # 3. Scaling
        scaler = StandardScaler()
        scaled_data = scaler.fit_transform(pdf)
        
        # 4. Train K-Means
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(scaled_data)
        
        # 5. Save Models
        joblib.dump(scaler, self.scaler_path)
        joblib.dump(kmeans, self.model_path)
        print(f"Model and Scaler saved to {self.models_dir}")
        
        # 6. Analyze Clusters (Profiling)
        pdf['cluster_id'] = cluster_labels
        
        # Merge back with original titles for sampling
        original_titles = [item["original_job"].get("title", "") for item in preprocessed]
        original_companies = [item["original_job"].get("company_name", "") for item in preprocessed]
        pdf['title'] = original_titles
        pdf['company'] = original_companies
        
        # Calculate cluster averages
        profile = pdf.groupby('cluster_id').mean(numeric_only=True).round(2)
        
        print("\n=== Cluster Profiles (Averages) ===")
        # Print key features for each cluster
        key_features = ['pay_amount', 'work_duration', 'is_short', 'is_weekend', 'is_admin', 'is_cs', 'is_food', 'is_physical', 'is_same_day_pay', 'is_insured']
        print(profile[key_features].to_string())
        
        print("\n=== Sample Jobs per Cluster ===")
        for i in range(k):
            print(f"\n[ Cluster {i} Samples ]")
            samples = pdf[pdf['cluster_id'] == i].head(5)
            for _, row in samples.iterrows():
                print(f"- {row['company']}: {row['title']} (시급: {row['pay_amount']}원, 기간: {row['work_duration']}시간)")
                
        return pdf, profile
        
if __name__ == "__main__":
    service = ClusteringService()
    pdf, profile = service.train_and_save_model(k=4)
