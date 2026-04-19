on add_bullets(body_item, bullet_lines)
	set AppleScript's text item delimiters to return
	set object text of body_item to bullet_lines as text
	set AppleScript's text item delimiters to ""
end add_bullets

set output_file to POSIX file "/Users/admin/Documents/house price prediction/house_price_prediction_presentation.pptx"

using terms from application "Keynote"
	tell application "Keynote"
		activate
		set deck to make new document with properties {document theme:theme "White"}
		
		tell deck
			set slide1 to make new slide with properties {base slide:master slide "Title & Subtitle"}
			tell slide1
				set object text of default title item to "House Price Prediction Project"
				set object text of default body item to "Notebook-based machine learning project using California housing data"
			end tell
			
			set slide2 to make new slide with properties {base slide:master slide "Title & Bullets"}
			tell slide2
				set object text of default title item to "Objectives"
				my add_bullets(default body item, {"Predict house prices from historical housing data", "Understand feature importance, missing values, and correlations", "Explain the ML workflow in a simple way", "Show the planned preprocessing and model evaluation flow"})
			end tell
			
			set slide3 to make new slide with properties {base slide:master slide "Title & Bullets"}
			tell slide3
				set object text of default title item to "Dataset Overview"
				my add_bullets(default body item, {"Dataset: California housing dataset", "Rows: 20,640 | Columns: 10", "Target: median_house_value", "Key features: location, rooms, bedrooms, population, households, median_income, ocean_proximity"})
			end tell
			
			set slide4 to make new slide with properties {base slide:master slide "Title & Bullets"}
			tell slide4
				set object text of default title item to "ML Model"
				my add_bullets(default body item, {"Preprocessing: missing-value imputation, one-hot encoding, and scaling", "Train/test split for evaluation", "Candidate models: Linear Regression, Ridge, Lasso, Random Forest, HistGradientBoosting", "Metrics: RMSE, MAE, and R-squared"})
			end tell
			
			set slide5 to make new slide with properties {base slide:master slide "Title & Bullets"}
			tell slide5
				set object text of default title item to "Architecture Diagram"
				set object text of default body item to "Housing CSV Data" & return & "->" & return & "EDA and Cleaning" & return & "->" & return & "Preprocessing" & return & "->" & return & "Train/Test Split" & return & "->" & return & "Model Training" & return & "->" & return & "Evaluation" & return & "->" & return & "Predicted House Price"
			end tell
			
			export deck to output_file as Microsoft PowerPoint
			close deck saving no
		end tell
	end tell
end using terms from
