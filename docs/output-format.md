This file lists the JSON structure for the model output files. When a model is run (or config) and the results should be compared with other results, it should generate an `output.json` file in that location which contains the following k-v pairs:

- name : Some identifier for the model, for example `"name": "CNN-2-Layer"`
- params : A dictionary of model parameters, for example `"params" : {"w1":..., "w2":..., }`
- val_loss : A list of validation losses recorded during training (every epoch)
- tr_loss : A list of training losses recorded during training (every epoch)

For the classification task (cloudy/clear) add the following:
- y : Input labels
- y_preds : Predicted labels from model

For the coverage task (pixel count) instead add:
- acc : List of testing accuracies; each value is the number of correct pixels out of the total.