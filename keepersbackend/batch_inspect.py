import os
from cleaning_check import inspect_cleaning_job

reference_dir = "reference_images"
postclean_dir = "postclean_images"
output_dir = "annotated"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Match files by naming pattern (e.g., reference_1.jpg with postclean_1.jpg)
for i in range(1, 100):  # Adjust range as needed
    ref_path = os.path.join(reference_dir, f"reference_{i}.jpg")
    post_path = os.path.join(postclean_dir, f"postclean_{i}.jpg")

    if os.path.exists(ref_path) and os.path.exists(post_path):
        job_id = f"batch_job_{i:03d}"
        result = inspect_cleaning_job(ref_path, post_path, job_id)
        print(f"{job_id} → {result['annotated_image']}")
