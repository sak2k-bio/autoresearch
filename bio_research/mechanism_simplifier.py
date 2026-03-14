"""
MechanismSimplifier module for AutoResearch Bio-Medical Pipeline
Transforms complex biochemical mechanisms into simple, visualizable chains
"""

import re
from typing import Dict, List, Tuple
from .config import config


class MechanismSimplifier:
    def __init__(self):
        # Biochemical process terminology mapping to simpler terms
        self.biochemical_mapping = {
            # Metabolic processes
            'glucose metabolism': 'energy processing',
            'glycolysis': 'sugar breakdown',
            'gluconeogenesis': 'sugar creation',
            'lipolysis': 'fat breakdown',
            'lipogenesis': 'fat creation',
            'beta oxidation': 'fat burning',
            'oxidative phosphorylation': 'energy production',
            'citric acid cycle': 'energy cycle',

            # Cellular processes
            'phosphorylation': 'activation tagging',
            'dephosphorylation': 'deactivation tagging',
            'acetylation': 'modification tagging',
            'methylation': 'gene tagging',
            'ubiquitination': 'destruction tagging',

            # Signaling pathways
            'signal transduction': 'cell messaging',
            'receptor binding': 'molecule recognition',
            'second messenger': 'internal signal',
            'kinase cascade': 'activation sequence',
            'transcription factor': 'gene activator',

            # Transport processes
            'active transport': 'energy-powered movement',
            'facilitated diffusion': 'assisted movement',
            'cotransport': 'partner movement',
            'symport': 'same-direction movement',
            'antiport': 'opposite-direction movement',

            # Protein processes
            'protein synthesis': 'protein building',
            'protein degradation': 'protein destruction',
            'post-translational modification': 'protein adjustment',
            'chaperone activity': 'protein helper',
        }

        # Complex terms to simplify
        self.complex_terms = {
            'reactive oxygen species': 'harmful oxygen molecules',
            'adenosine triphosphate': 'cellular energy (ATP)',
            'nicotinamide adenine dinucleotide': 'energy carrier (NAD)',
            'coenzyme A': 'energy molecule (CoA)',
            'cyclic adenosine monophosphate': 'cellular signal (cAMP)',
            'inositol trisphosphate': 'calcium signal (IP3)',
            'diacylglycerol': 'cellular activator (DAG)',

            # Enzymes (generalized)
            'kinase': 'activation enzyme',
            'phosphatase': 'deactivation enzyme',
            'synthase': 'building enzyme',
            'transferase': 'moving enzyme',
            'hydrolase': 'breaking enzyme',
            'oxidoreductase': 'electron transfer enzyme',
            'ligase': 'joining enzyme',
        }

    def simplify_mechanism(self, mechanism: str, mechanistic_chain: str = "") -> Dict[str, str]:
        """
        Simplify a complex biochemical mechanism

        Args:
            mechanism: Original complex mechanism
            mechanistic_chain: Original mechanistic chain

        Returns:
            Dictionary with simplified versions
        """
        simplified = {
            'simple_mechanism': self._simplify_text(mechanism),
            'simple_chain': self._simplify_chain(mechanistic_chain) if mechanistic_chain else self._extract_and_simplify_chain(mechanism),
            'visualizable_sequence': self._create_visualizable_sequence(mechanism),
            'analogy': self._create_analogy(mechanism)
        }

        return simplified

    def _simplify_text(self, text: str) -> str:
        """
        Replace complex biochemical terms with simpler equivalents
        """
        simplified = text.lower()

        # Replace complex processes
        for complex_term, simple_term in self.biochemical_mapping.items():
            simplified = re.sub(r'\b' + re.escape(complex_term) + r'\b', simple_term, simplified, flags=re.IGNORECASE)

        # Replace complex molecules
        for complex_term, simple_term in self.complex_terms.items():
            simplified = re.sub(r'\b' + re.escape(complex_term) + r'\b', simple_term, simplified, flags=re.IGNORECASE)

        # Capitalize first letter
        if simplified:
            simplified = simplified[0].upper() + simplified[1:]

        return simplified

    def _simplify_chain(self, chain: str) -> str:
        """
        Simplify a mechanistic chain
        """
        if not chain:
            return ""

        # Split by arrows or separators
        elements = re.split(r' ?(?:→|->|=>|,) ?', chain)

        simplified_elements = []
        for element in elements:
            element = element.strip()
            simplified_element = self._simplify_single_element(element)
            simplified_elements.append(simplified_element)

        return " → ".join(simplified_elements)

    def _extract_and_simplify_chain(self, mechanism: str) -> str:
        """
        Extract and simplify a mechanistic chain from mechanism text
        """
        # Look for cause-effect relationships in the text
        # Patterns for cause-effect relationships
        patterns = [
            r"(\w+(?:\s+\w+)*)\s+(?:leads to|results in|causes|triggers|activates|stimulates|promotes)\s+(\w+(?:\s+\w+)*)",
            r"(\w+(?:\s+\w+)*)\s*→\s*(\w+(?:\s+\w+)*)",
            r"first\s+(\w+(?:\s+\w+)*)\s+then\s+(\w+(?:\s+\w+)*)",
        ]

        chain_elements = []
        for pattern in patterns:
            matches = re.finditer(pattern, mechanism, re.IGNORECASE)
            for match in matches:
                cause = self._simplify_single_element(match.group(1))
                effect = self._simplify_single_element(match.group(2))

                if not chain_elements or chain_elements[-1] != cause:
                    chain_elements.append(cause)
                chain_elements.append(effect)

        # Remove duplicates while preserving order
        seen = set()
        unique_elements = []
        for elem in chain_elements:
            if elem.lower() not in seen:
                seen.add(elem.lower())
                unique_elements.append(elem)

        return " → ".join(unique_elements) if unique_elements else ""

    def _simplify_single_element(self, element: str) -> str:
        """
        Simplify a single element in a chain
        """
        simplified = element.lower().strip()

        # Replace complex processes
        for complex_term, simple_term in self.biochemical_mapping.items():
            simplified = re.sub(r'\b' + re.escape(complex_term) + r'\b', simple_term, simplified, flags=re.IGNORECASE)

        # Replace complex molecules
        for complex_term, simple_term in self.complex_terms.items():
            simplified = re.sub(r'\b' + re.escape(complex_term) + r'\b', simple_term, simplified, flags=re.IGNORECASE)

        # Capitalize first letter
        if simplified:
            simplified = simplified[0].upper() + simplified[1:]

        return simplified

    def _create_visualizable_sequence(self, mechanism: str) -> str:
        """
        Create a sequence that's easy to visualize
        """
        # Extract key components and arrange them in a logical sequence
        sentences = mechanism.split('.')
        for sentence in sentences:
            if any(word in sentence.lower() for word in ['process', 'sequence', 'pathway', 'cascade']):
                # Look for ordered relationships
                sequence_elements = self._find_sequence_elements(sentence)
                if sequence_elements:
                    return " → ".join(sequence_elements)

        # If no specific sequence found, use the simplified chain
        return self._extract_and_simplify_chain(mechanism)

    def _find_sequence_elements(self, text: str) -> List[str]:
        """
        Find sequence elements in text
        """
        # Look for ordered processes
        sequence_words = ['first', 'then', 'next', 'after', 'before', 'subsequently', 'finally']
        elements = []

        # Split by sequence indicators
        for word in sequence_words:
            if word in text.lower():
                # This is a simplified approach - in practice, you'd want more sophisticated NLP
                parts = re.split(r'\b' + word + r'\b', text, flags=re.IGNORECASE)
                for part in parts:
                    part = part.strip()
                    if len(part) > 5:  # Meaningful text
                        simplified = self._simplify_single_element(part)
                        if simplified and simplified not in elements:
                            elements.append(simplified)

        return elements

    def _create_analogy(self, mechanism: str) -> str:
        """
        Create an analogy to help understand the mechanism
        """
        # Identify the type of mechanism and create an appropriate analogy
        if any(word in mechanism.lower() for word in ['transport', 'movement', 'flow']):
            return "Think of it like a conveyor belt system in a factory, where molecules are moved from station to station for processing."

        if any(word in mechanism.lower() for word in ['signaling', 'communication', 'response']):
            return "Think of it like a chain of phone calls, where one person receives a message and passes it along to the next person."

        if any(word in mechanism.lower() for word in ['regulation', 'control', 'balance']):
            return "Think of it like a thermostat controlling a heating system, adjusting based on feedback to maintain balance."

        if any(word in mechanism.lower() for word in ['energy', 'atp', 'metabolism']):
            return "Think of it like a power plant generating electricity, where raw materials are converted into usable energy."

        if any(word in mechanism.lower() for word in ['activation', 'switch', 'turn on']):
            return "Think of it like a series of light switches, where flipping one switch turns on the next one in line."

        # Generic analogy
        return "Think of it like an assembly line, where each step builds upon the previous one to create the final product."


# Example usage:
if __name__ == "__main__":
    simplifier = MechanismSimplifier()

    # Example complex mechanism
    complex_mechanism = """
    Insulin resistance develops when nutrient excess leads to mitochondrial dysfunction,
    which increases reactive oxygen species production. This oxidative stress then inhibits
    insulin receptor substrate phosphorylation, reducing downstream Akt activation.
    Consequently, glucose transporter translocation to the cell membrane is impaired,
    leading to elevated blood glucose levels.
    """

    simplified = simplifier.simplify_mechanism(complex_mechanism)

    print("Original mechanism:")
    print(complex_mechanism)
    print("\nSimplified mechanism:")
    print(simplified['simple_mechanism'])
    print("\nSimple chain:")
    print(simplified['simple_chain'])
    print("\nVisualizable sequence:")
    print(simplified['visualizable_sequence'])
    print("\nAnalogy:")
    print(simplified['analogy'])