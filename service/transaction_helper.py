def determine_shaketag(transaction: dict) -> str:
	return (transaction.get('to') or transaction['from'])['label']

def determine_swap_amnt(transaction: dict) -> float:
	swap = 1. if (transaction['direction'] == 'credit') else -1.
	swap = swap * float(f'{transaction["amount"]:.2f}')

	return swap
