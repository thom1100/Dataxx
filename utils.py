# Fonction pour trier les sponsors selon les critères
def sort_sponsors(sponsors_list, reference_region=None):
    """
    Trie les sponsors:
    1. Les sponsors de la même région en premier
    2. Ensuite par ordre décroissant de montant/chiffre d'affaires
    """
    if not isinstance(sponsors_list, list):
        return sponsors_list

    def extract_amount(sponsor):
        """Extrait le montant d'un sponsor pour le tri"""
        # Cherche différents champs possibles pour le montant
        amount_fields = ['Chiffre_d_affaires', 'Amount', 'Montant', 'Amount invested yearly']
        for field in amount_fields:
            if field in sponsor:
                value = sponsor[field]
                if isinstance(value, (int, float)):
                    return value
                elif isinstance(value, str):
                    # Essaie d'extraire le nombre d'une chaîne comme "10M€"
                    try:
                        return float(value.replace('M€', '').replace('€', '').replace(' ', ''))
                    except:
                        pass
        return 0

    def is_same_region(sponsor):
        """Vérifie si le sponsor est de la même région"""
        if not reference_region:
            return False
        return sponsor.get('Region', '').lower() == reference_region.lower()

    # Trie: d'abord par région (même région en premier), puis par montant décroissant
    sorted_list = sorted(sponsors_list, key=lambda x: (not is_same_region(x), -extract_amount(x)))
    return sorted_list