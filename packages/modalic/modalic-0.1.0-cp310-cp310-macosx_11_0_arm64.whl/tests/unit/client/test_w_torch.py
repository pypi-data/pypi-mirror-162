#  Copyright (c) modalic 2022. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at:
#
#       https://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
#  or implied. See the License for the specific language governing
#  permissions and limitations under the License.

# import sklearn.datasets as datasets
#
#
# @pytest.fixture(scope="module")
# def data():
#     iris = datasets.load_iris()
#     data = pd.DataFrame(
#         data=np.c_[iris["data"], iris["target"]], columns=iris["feature_names"] + ["target"]
#     )
#     y = data["target"]
#     x = data.drop("target", axis=1)
#     yield x, y
