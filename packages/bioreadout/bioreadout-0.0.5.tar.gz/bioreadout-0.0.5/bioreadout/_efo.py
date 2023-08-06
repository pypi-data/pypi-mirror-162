from functools import cached_property

import pandas as pd
from bionty import EntityTable, Ontology
from bionty._settings import settings


class EFO(EntityTable):
    """Experimental Factor Ontology.

    https://www.ebi.ac.uk/ols/ontologies/efo
    """

    def __init__(self, reload=False) -> None:
        self._reload = reload
        self._prefix = "http://www.ebi.ac.uk/efo/"
        self._readout_terms = {
            "assay": "OBI:0000070",
            "assay_by_molecule": "EFO:0002772",
            "assay_by_instrument": "EFO:0002773",
            "assay_by_sequencer": "EFO:0003740",
            "measurement": "EFO:0001444",
        }

    @cached_property
    def df(self) -> pd.DataFrame:
        """DataFrame."""
        return pd.DataFrame(
            [
                (term.id.replace(self._prefix, "").replace("_", ":"), term.name)
                for term in self.ontology.terms()
                if term.id.startswith(("EFO:", self._prefix))
            ],
            columns=["id", "name"],
        ).set_index("id")

    @cached_property
    def ontology(self):
        """Cell ontology."""
        url = "http://www.ebi.ac.uk/efo/efo.owl"
        localpath = settings.dynamicdir / "efo.obo"
        url = url if ((not localpath.exists()) or (self._reload)) else None
        ontology_ = Ontology(handle=localpath, url=url, prefix=self._prefix)
        if url is not None:
            ontology_.write_obo()
        return ontology_

    @cached_property
    def assay(self):
        """Assays OBI:0000070."""
        return self.ontology._list_subclasses(self._readout_terms["assay"])

    @cached_property
    def assay_by_molecule(self):
        """Assays by molecule EFO:0002772."""
        return self.ontology._list_subclasses(self._readout_terms["assay_by_molecule"])

    @cached_property
    def assay_by_instrument(self):
        """Assays by instrument EFO:0002773."""
        return self.ontology._list_subclasses(
            self._readout_terms["assay_by_instrument"]
        )

    @cached_property
    def assay_by_sequencer(self):
        """Assay by sequencer EFO:0003740."""
        return self.ontology._list_subclasses(self._readout_terms["assay_by_sequencer"])

    @cached_property
    def measurement(self):
        """Measurement EFO:0001444."""
        return self.ontology._list_subclasses(self._readout_terms["measurement"])

    def get_readout_type(self, term_id):
        """Get readout_type attributes from EFO id."""
        term = self.ontology.get_term(term_id)
        superclasses = term.superclasses()

        # get the molecule term
        molecules = [i for i in self.assay_by_molecule if i in superclasses]
        # get the instrument term
        instruments = [i for i in self.assay_by_sequencer if i in superclasses]
        if len(instruments) == 0:
            instruments = [i for i in self.assay_by_instrument if i in superclasses]
        # get the measurement for non-molecular readouts
        measurements = [i for i in self.measurement if i in superclasses]

        molecule = None if len(molecules) == 0 else [i.name for i in molecules]
        instrument = None if len(instruments) == 0 else [i.name for i in instruments]
        measurement = None if len(measurements) == 0 else [i.name for i in measurements]

        readout_type = {
            "efo_id": term_id,
            "name": term.name,
            "molecule": molecule,
            "instrument": instrument,
            "measurement": measurement,
        }

        return readout_type


def readout_type(efo_id: str):
    """Get readout_type attributes from EFO id."""
    return EFO().get_readout_type(term_id=efo_id)
