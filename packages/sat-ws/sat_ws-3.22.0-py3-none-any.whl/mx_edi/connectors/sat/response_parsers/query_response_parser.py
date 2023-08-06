from typing import Dict

import xmltodict

from .response_parser import ResponseParser


class QueryParser(ResponseParser):
    @staticmethod
    def parse(response: str) -> Dict[str, str]:
        """Gets the Query ID from the raw response"""
        response_dict = xmltodict.parse(response)
        result = response_dict["Envelope"]["Body"]["SolicitaDescargaResponse"][
            "SolicitaDescargaResult"
        ]
        return {
            "CodEstatus": result["@CodEstatus"],
            "IdSolicitud": result.get("@IdSolicitud"),
        }
