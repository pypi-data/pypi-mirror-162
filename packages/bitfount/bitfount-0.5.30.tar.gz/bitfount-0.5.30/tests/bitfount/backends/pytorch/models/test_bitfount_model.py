"""Test PyTorchBitfountModel."""
import os
from pathlib import Path
from typing import Type
from unittest.mock import Mock

import numpy as np
from pytest import fixture, raises
from pytest_mock import MockerFixture
import pytorch_lightning as pl
import torch
from torchmetrics.functional import jaccard_index

from bitfount.backends.pytorch.models.bitfount_model import PyTorchBitfountModel
from bitfount.data.datasets import _BitfountDataset
from bitfount.data.datasources.base_source import BaseSource
from bitfount.data.datasources.dataframe_source import DataFrameSource
from bitfount.data.datasplitters import PercentageSplitter
from bitfount.data.datastructure import DataStructure
from bitfount.data.schema import BitfountSchema
from bitfount.data.types import DataSplit
from bitfount.federated.model_reference import BitfountModelReference
from bitfount.federated.modeller import _Modeller
from bitfount.hub.api import BitfountHub
from bitfount.metrics import (
    BINARY_CLASSIFICATION_METRICS,
    MetricCollection,
    MetricsProblem,
)
from bitfount.models.base_models import ModelContext
from bitfount.utils import _get_non_abstract_classes_from_module
from tests.bitfount import TEST_SECURITY_FILES
from tests.bitfount.backends.pytorch.helper import get_params_mean
from tests.bitfount.models.test_models import SERIALIZED_MODEL_NAME
from tests.utils.helper import (
    AUC_THRESHOLD,
    TABLE_NAME,
    backend_test,
    create_dataset,
    create_datasource,
    create_datastructure,
    create_query_datastructure,
    create_schema,
    create_segmentation_dataset,
    integration_test,
    unit_test,
)


@backend_test
class TestPyTorchBitfountModel:
    """Test PyTorchBitfountModel class."""

    @fixture
    def datastructure(self) -> DataStructure:
        """Fixture for datastructure."""
        return create_datastructure()

    @fixture
    def query_datastructure(self) -> DataStructure:
        """Fixture for datastructure containing query."""
        return create_query_datastructure()

    @fixture
    def datasource(self) -> BaseSource:
        """Fixture for datasource."""
        return create_datasource(classification=True)

    @fixture
    def dummy_model_class(
        self, pytorch_bitfount_model_correct_structure: str, tmp_path: Path
    ) -> type:
        """Returns Dummy PytorchBitfountModel class."""
        model_file = tmp_path / "DummyModel.py"
        model_file.touch()
        model_file.write_text(pytorch_bitfount_model_correct_structure)
        return _get_non_abstract_classes_from_module(model_file)["DummyModel"]

    @fixture
    def dummy_model_class_tab_and_img(
        self, pytorch_bitfount_model_tab_image_data: str, tmp_path: Path
    ) -> type:
        """Returns Dummy PytorchBitfountModel class."""
        model_file = tmp_path / "DummyModelTabImg.py"
        model_file.touch()
        model_file.write_text(pytorch_bitfount_model_tab_image_data)
        return _get_non_abstract_classes_from_module(model_file)["DummyModelTabImg"]

    @integration_test
    def test_dummy_model_works_correctly(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
    ) -> None:
        """Test fit() method runs without failure."""
        model = dummy_model_class(
            datastructure=datastructure, schema=create_schema(classification=True)
        )
        model._pl_trainer = pl.Trainer(fast_dev_run=True)
        model.fit(datasource)

    @unit_test
    def test_dummy_model_img_tab_works_correctly(
        self,
        dummy_model_class_tab_and_img: type,
    ) -> None:
        """Test fit() method runs without failure for image&tabular tabular dataset."""
        data = create_dataset(classification=True, image=True)
        ds = DataFrameSource(data[:100])
        model = dummy_model_class_tab_and_img(
            datastructure=DataStructure(
                target="TARGET", image_cols=["image"], table=TABLE_NAME
            ),
            schema=create_schema(classification=True),
        )
        model._pl_trainer = pl.Trainer(fast_dev_run=True)
        model.fit(ds)

    @integration_test
    def test_dummy_model_learns(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
    ) -> None:
        """Test that the model learns by checking metrics."""
        model = dummy_model_class(
            datastructure=datastructure, schema=create_schema(classification=True)
        )
        model.fit(datasource)
        preds, target = model.evaluate()

        # TODO: [BIT-1604] Remove these assert statements once they become superfluous.
        assert isinstance(preds, np.ndarray)
        assert isinstance(target, np.ndarray)

        metrics = MetricCollection.create_from_model(model)
        results = metrics.compute(target, preds)
        assert isinstance(results, dict)
        assert len(metrics.metrics) == len(BINARY_CLASSIFICATION_METRICS)
        assert results["AUC"] > AUC_THRESHOLD

    @unit_test
    def test_init_no_classes_raises_error(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
    ) -> None:
        """Test initialise fails with no n_classes specified and no target."""
        datasource.load_data()
        inference_datasource = DataFrameSource(datasource.data, ignore_cols=["TARGET"])
        inference_datastructure = datastructure
        inference_datastructure.target = None
        inference_model = dummy_model_class(
            datastructure=datastructure,
            schema=BitfountSchema(
                inference_datasource,
                ignore_cols={TABLE_NAME: ["TARGET"]},
                table_name=TABLE_NAME,
            ),
            epochs=1,
        )
        with raises(ValueError):
            inference_model.initialise_model()

    @unit_test
    def test_prediction(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
    ) -> None:
        """Test that model prediction works after training."""
        model = dummy_model_class(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            epochs=1,
        )
        model.fit(datasource)
        model.predict(datasource)

    @unit_test
    def test_initialise_with_context(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
    ) -> None:
        """Test that model prediction works after training."""
        model = dummy_model_class(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            epochs=1,
        )
        model.initialise_model(datasource, context=ModelContext.WORKER)

    @unit_test
    def test_prediction_empty_testset(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
    ) -> None:
        """Test that model evaluation fails on empty dataset."""
        model = dummy_model_class(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            epochs=1,
        )
        model.fit(datasource)
        empty_datasource = DataFrameSource(
            datasource.data, data_splitter=PercentageSplitter(0, 0)
        )
        with raises(ValueError):
            model.predict(empty_datasource)

    @integration_test
    def test_prediction_with_unsupervised_data(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
        mocker: MockerFixture,
        tmp_path: Path,
    ) -> None:
        """Test that model evaluation works.

        Test that predict() method works, after training and deserialization.
        Sets the n_classes field explicitly with no TARGET field present
        in the data.
        """
        model = dummy_model_class(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            epochs=1,
        )
        model.fit(datasource)
        model.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        inference_datasource = DataFrameSource(datasource.data, ignore_cols=["TARGET"])
        inference_datastructure = datastructure
        inference_datastructure.target = None
        inference_datastructure.selected_cols.remove("TARGET")
        inference_datastructure._force_stype.pop("categorical")
        inference_model = dummy_model_class(
            datastructure=inference_datastructure,
            schema=BitfountSchema(
                inference_datasource,
                ignore_cols={TABLE_NAME: ["TARGET"]},
                table_name=TABLE_NAME,
            ),
            n_classes=2,
            epochs=1,
        )
        inference_model.deserialize(tmp_path / SERIALIZED_MODEL_NAME)
        preds = inference_model.predict(inference_datasource)

        mocker.patch.object(_BitfountDataset, "_set_column_name_attributes")
        mocker.patch.object(_BitfountDataset, "_reformat_data")
        dataset = _BitfountDataset(
            inference_datasource, Mock(value="test"), Mock(), Mock(), Mock()
        )

        assert preds is not None
        assert len(preds) == len(dataset.get_dataset_split(DataSplit.TEST))
        assert inference_model.n_classes == len(preds[0])

    @unit_test
    def test_serialization_before_fitting(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
        tmp_path: Path,
    ) -> None:
        """Test Model can be serialized properly before fitting."""
        model = dummy_model_class(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": "TARGET"}},
                table_name=TABLE_NAME,
            ),
        )
        model.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME) is True

    @unit_test
    def test_serialization_after_fitting(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
        tmp_path: Path,
    ) -> None:
        """Test Model can be serialized properly after fitting."""
        model = dummy_model_class(
            datastructure=datastructure, schema=create_schema(classification=True)
        )
        model.fit(data=datasource)
        model.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME) is True

    @unit_test
    def test_deserialization_before_fitting(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
        tmp_path: Path,
    ) -> None:
        """Test Model can be deserialized properly before fitting."""
        model = dummy_model_class(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
        )
        model.fit(data=datasource)
        model.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME) is True
        model2 = dummy_model_class(
            datastructure=datastructure,
            schema=BitfountSchema(
                datasource,
                force_stypes={TABLE_NAME: {"categorical": ["TARGET"]}},
                table_name=TABLE_NAME,
            ),
            seed=123,
        )
        model2.deserialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert torch.isclose(
            get_params_mean(model.get_param_states()),
            get_params_mean(model2.get_param_states()),
            atol=1e-4,
        )

    @unit_test
    def test_deserialization_after_fitting(
        self,
        datasource: DataFrameSource,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
        tmp_path: Path,
    ) -> None:
        """Test Model can be deserialized properly after fitting."""
        model = dummy_model_class(
            datastructure=datastructure, schema=create_schema(classification=True)
        )
        model.fit(data=datasource)
        model.serialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert os.path.exists(tmp_path / SERIALIZED_MODEL_NAME) is True
        model2 = dummy_model_class(
            datastructure=datastructure,
            schema=create_schema(classification=True),
            seed=123,
        )
        model2.fit(data=datasource)
        model2.deserialize(tmp_path / SERIALIZED_MODEL_NAME)
        assert torch.isclose(
            get_params_mean(model.get_param_states()),
            get_params_mean(model2.get_param_states()),
            atol=1e-4,
        )

    @unit_test
    def test__get_import_statements(
        self,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
    ) -> None:
        """Test _get_import_statements."""
        model = dummy_model_class(
            datastructure=datastructure, schema=create_schema(classification=True)
        )
        assert model._get_import_statements() == [
            "import os",
            "import torch",
            "from torch import nn as nn",
            "from torch.nn import functional as F",
            "from bitfount import *",
            "import bitfount",
        ]

    @unit_test
    def test__get_model(
        self,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
        mocker: MockerFixture,
    ) -> None:
        """Tests private _get_model method with a custom model.

        Checks that a BitfountModelReference is created from the custom model.
        """
        model = dummy_model_class(
            datastructure=datastructure, schema=create_schema(classification=True)
        )
        # Mock the serialization of the model
        mock_serialize_method = mocker.patch.object(
            model, "serialize_model_source_code"
        )
        extra_imports = ["from blah import blah"]
        model_ref = model._get_model(
            extra_imports=extra_imports,
            hub=Mock(spec=BitfountHub, username="test"),
        )
        assert isinstance(model_ref, BitfountModelReference)
        mock_serialize_method.assert_called_once_with(
            filename="DummyModel.py", extra_imports=extra_imports
        )

    @unit_test
    def test__fit_federated(
        self,
        datastructure: DataStructure,
        dummy_model_class: Type[PyTorchBitfountModel],
        mock_bitfount_session: Mock,
        mocker: MockerFixture,
    ) -> None:
        """Tests private _fit_federated method with a custom model.

        Checks that DistributedModelMixIn._fit_federated helper method creates
        correct instances and runs the modeller correctly.
        """
        # Create model to test
        model = dummy_model_class(
            datastructure=datastructure, schema=create_schema(classification=True)
        )

        # Mock the serialization of the model
        mock_serialize_method = mocker.patch.object(
            model,
            "serialize_model_source_code",
            return_value="This is some source code",
        )

        # Patch out the modeller's run method as we only care how it is called
        # from _fit_federated.
        mock_modeller_run_method = mocker.patch.object(_Modeller, "run")

        # Run method
        pod_identifiers = ["bitfount/census-income", "bitfount/census-income-2"]
        model._fit_federated(
            pod_identifiers=pod_identifiers,
            private_key_or_file=TEST_SECURITY_FILES / "test_private.testkey",
        )

        # Check run method was called correctly
        # TODO: [BIT-983] Should this check that the Modeller was instantiated
        #       correctly? Related to whether we should mock out the helper calls.
        mock_modeller_run_method.assert_called_once_with(
            pod_identifiers, require_all_pods=False, model_out=None
        )
        mock_serialize_method.assert_called_once_with(
            filename="DummyModel.py", extra_imports=None
        )


@backend_test
class TestUNetPyTorchBitfountModel:
    """Test PyTorchBitfountModel class."""

    @fixture
    def dummy_model_class(
        self, pytorch_bitfount_segmentation_model: str, tmp_path: Path
    ) -> type:
        """Returns Dummy PytorchBitfountModel class."""
        model_file = tmp_path / "DummyUnet.py"
        model_file.touch()
        model_file.write_text(pytorch_bitfount_segmentation_model)
        return _get_non_abstract_classes_from_module(model_file)["DummyUnet"]

    @unit_test
    def test_dummy_model_works(
        self, dummy_model_class: Type[PyTorchBitfountModel], tmp_path: Path
    ) -> None:
        """Tests that the segmentation model works."""
        seg_dir = tmp_path / "seg/"
        seg_dir.mkdir()
        seg_dataset = create_segmentation_dataset(seg_dir=seg_dir)
        ds = DataStructure(
            table=TABLE_NAME, image_cols=["img", "masks"], target="masks"
        )
        datasource = DataFrameSource(seg_dataset)
        schema = BitfountSchema(
            datasource,
            force_stypes={TABLE_NAME: {"image": ["img", "masks"]}},
            table_name=TABLE_NAME,
        )
        model = dummy_model_class(
            n_channels=3,
            n_classes=3,
            datastructure=ds,
            schema=schema,
            steps=1,
            batch_size=5,
        )
        model.fit(datasource)

    @integration_test
    def test_dummy_model_learns(
        self, dummy_model_class: Type[PyTorchBitfountModel], tmp_path: Path
    ) -> None:
        """Tests the segmentation model learns by checking metrics."""
        seg_dir = tmp_path / "seg/"
        seg_dir.mkdir()
        seg_dataset = create_segmentation_dataset(seg_dir=seg_dir)
        ds = DataStructure(
            table=TABLE_NAME, image_cols=["img", "masks"], target="masks"
        )
        datasource = DataFrameSource(seg_dataset)
        schema = BitfountSchema(
            datasource,
            force_stypes={TABLE_NAME: {"image": ["img", "masks"]}},
            table_name=TABLE_NAME,
        )
        model = dummy_model_class(
            n_channels=3,
            n_classes=3,
            datastructure=ds,
            schema=schema,
            epochs=1,
            batch_size=5,
        )
        model.fit(datasource)
        preds, target = model.evaluate()

        # TODO: [BIT-1604] Remove these assert statements once they become superfluous.
        assert isinstance(preds, np.ndarray)
        assert isinstance(target, np.ndarray)

        metrics = MetricCollection(MetricsProblem.SEGMENTATION)
        results = metrics.compute(target, preds)

        assert len(results) == 3
        # Confirm that our IoU metric matches the pytorch implementation.
        assert (
            round(
                jaccard_index(torch.tensor(preds), torch.tensor(target), num_classes=3)
                .numpy()
                .tolist(),
                4,
            )
            == results["IoU"]
        )
