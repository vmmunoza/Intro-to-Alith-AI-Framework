import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackContext,
    CallbackQueryHandler
)
from alith import Agent
from web3 import Web3
from eth_account import Account
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Metis Sepolia Configuration
METIS_SEPOLIA_CONFIG = {
    'chain_id': 59902,
    'rpc_url': 'https://sepolia.metisdevops.link',
    'explorer_url': 'https://sepolia-explorer.metisdevops.link',
    'name': 'Metis Sepolia'
}

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(METIS_SEPOLIA_CONFIG['rpc_url']))

# ERC20 ABI
ERC20_ABI = '''[
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "name",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "symbol",
                "type": "string"
            },
            {
                "internalType": "uint256",
                "name": "initialSupply",
                "type": "uint256"
            },
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "account",
                "type": "address"
            }
        ],
        "name": "balanceOf",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "decimals",
        "outputs": [
            {
                "internalType": "uint8",
                "name": "",
                "type": "uint8"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "totalSupply",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]'''

# ERC721 ABI (Basic NFT)
ERC721_ABI = '''[
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "name",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "symbol",
                "type": "string"
            },
            {
                "internalType": "string",
                "name": "baseURI",
                "type": "string"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "name",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "symbol",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]'''

# ERC1155 ABI (Multi Token)
ERC1155_ABI = '''[
    {
        "inputs": [
            {
                "internalType": "string",
                "name": "uri_",
                "type": "string"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "uri",
        "outputs": [
            {
                "internalType": "string",
                "name": "",
                "type": "string"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    }
]'''

# Smart Contract Bytecode (placeholders - you would need the actual deployment bytecode)
ERC20_BYTECODE = "0x608060405234801562000010575f80fd5b506040516200180938038062001809833981810160405281019062000036919062000546565b8383816003908162000049919062000821565b5080600490816200005b919062000821565b5050506200007081836200007a60201b60201c565b50505050620009ff565b5f73ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff1603620000ed575f6040517fec442f05000000000000000000000000000000000000000000000000000000008152600401620000e4919062000916565b60405180910390fd5b620001005f83836200010460201b60201c565b5050565b5f73ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff160362000158578060025f8282546200014b91906200095e565b9250508190555062000229565b5f805f8573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f2054905081811015620001e4578381836040517fe450d38c000000000000000000000000000000000000000000000000000000008152600401620001db93929190620009a9565b60405180910390fd5b8181035f808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f2081905550505b5f73ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff160362000272578060025f8282540392505081905550620002bc565b805f808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f205f82825401925050819055505b8173ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef836040516200031b9190620009e4565b60405180910390a3505050565b5f604051905090565b5f80fd5b5f80fd5b5f80fd5b5f80fd5b5f601f19601f8301169050919050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52604160045260245ffd5b620003898262000341565b810181811067ffffffffffffffff82111715620003ab57620003aa62000351565b5b80604052505050565b5f620003bf62000328565b9050620003cd82826200037e565b919050565b5f67ffffffffffffffff821115620003ef57620003ee62000351565b5b620003fa8262000341565b9050602081019050919050565b5f5b838110156200042657808201518184015260208101905062000409565b5f8484015250505050565b5f620004476200044184620003d2565b620003b4565b9050828152602081018484840111156200046657620004656200033d565b5b6200047384828562000407565b509392505050565b5f82601f83011262000492576200049162000339565b5b8151620004a484826020860162000431565b91505092915050565b5f819050919050565b620004c181620004ad565b8114620004cc575f80fd5b50565b5f81519050620004df81620004b6565b92915050565b5f73ffffffffffffffffffffffffffffffffffffffff82169050919050565b5f6200051082620004e5565b9050919050565b620005228162000504565b81146200052d575f80fd5b50565b5f81519050620005408162000517565b92915050565b5f805f806080858703121562000561576200056062000331565b5b5f85015167ffffffffffffffff81111562000581576200058062000335565b5b6200058f878288016200047b565b945050602085015167ffffffffffffffff811115620005b357620005b262000335565b5b620005c1878288016200047b565b9350506040620005d487828801620004cf565b9250506060620005e78782880162000530565b91505092959194509250565b5f81519050919050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52602260045260245ffd5b5f60028204905060018216806200064257607f821691505b602082108103620006585762000657620005fd565b5b50919050565b5f819050815f5260205f209050919050565b5f6020601f8301049050919050565b5f82821b905092915050565b5f60088302620006bc7fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff826200067f565b620006c886836200067f565b95508019841693508086168417925050509392505050565b5f819050919050565b5f6200070962000703620006fd84620004ad565b620006e0565b620004ad565b9050919050565b5f819050919050565b6200072483620006e9565b6200073c620007338262000710565b8484546200068b565b825550505050565b5f90565b6200075262000744565b6200075f81848462000719565b505050565b5b8181101562000786576200077a5f8262000748565b60018101905062000765565b5050565b601f821115620007d5576200079f816200065e565b620007aa8462000670565b81016020851015620007ba578190505b620007d2620007c98562000670565b83018262000764565b50505b505050565b5f82821c905092915050565b5f620007f75f1984600802620007da565b1980831691505092915050565b5f620008118383620007e6565b9150826002028217905092915050565b6200082c82620005f3565b67ffffffffffffffff81111562000848576200084762000351565b5b6200085482546200062a565b620008618282856200078a565b5f60209050601f83116001811462000897575f841562000882578287015190505b6200088e858262000804565b865550620008fd565b601f198416620008a7866200065e565b5f5b82811015620008d057848901518255600182019150602085019450602081019050620008a9565b86831015620008f05784890151620008ec601f891682620007e6565b8355505b6001600288020188555050505b505050505050565b620009108162000504565b82525050565b5f6020820190506200092b5f83018462000905565b92915050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52601160045260245ffd5b5f6200096a82620004ad565b91506200097783620004ad565b925082820190508082111562000992576200099162000931565b5b92915050565b620009a381620004ad565b82525050565b5f606082019050620009be5f83018662000905565b620009cd602083018562000998565b620009dc604083018462000998565b949350505050565b5f602082019050620009f95f83018462000998565b92915050565b610dfc8062000a0d5f395ff3fe608060405234801561000f575f80fd5b5060043610610091575f3560e01c8063313ce56711610064578063313ce5671461013157806370a082311461014f57806395d89b411461017f578063a9059cbb1461019d578063dd62ed3e146101cd57610091565b806306fdde0314610095578063095ea7b3146100b357806318160ddd146100e357806323b872dd14610101575b5f80fd5b61009d6101fd565b6040516100aa9190610a75565b60405180910390f35b6100cd60048036038101906100c89190610b26565b61028d565b6040516100da9190610b7e565b60405180910390f35b6100eb6102af565b6040516100f89190610ba6565b60405180910390f35b61011b60048036038101906101169190610bbf565b6102b8565b6040516101289190610b7e565b60405180910390f35b6101396102e6565b6040516101469190610c2a565b60405180910390f35b61016960048036038101906101649190610c43565b6102ee565b6040516101769190610ba6565b60405180910390f35b610187610333565b6040516101949190610a75565b60405180910390f35b6101b760048036038101906101b29190610b26565b6103c3565b6040516101c49190610b7e565b60405180910390f35b6101e760048036038101906101e29190610c6e565b6103e5565b6040516101f49190610ba6565b60405180910390f35b60606003805461020c90610cd9565b80601f016020809104026020016040519081016040528092919081815260200182805461023890610cd9565b80156102835780601f1061025a57610100808354040283529160200191610283565b820191905f5260205f20905b81548152906001019060200180831161026657829003601f168201915b5050505050905090565b5f80610297610467565b90506102a481858561046e565b600191505092915050565b5f600254905090565b5f806102c2610467565b90506102cf858285610480565b6102da858585610513565b60019150509392505050565b5f6012905090565b5f805f8373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f20549050919050565b60606004805461034290610cd9565b80601f016020809104026020016040519081016040528092919081815260200182805461036e90610cd9565b80156103b95780601f10610390576101008083540402835291602001916103b9565b820191905f5260205f20905b81548152906001019060200180831161039c57829003601f168201915b5050505050905090565b5f806103cd610467565b90506103da818585610513565b600191505092915050565b5f60015f8473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f205f8373ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f2054905092915050565b5f33905090565b61047b8383836001610603565b505050565b5f61048b84846103e5565b90507fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff81101561050d57818110156104fe578281836040517ffb8f41b20000000000000000000000000000000000000000000000000000000081526004016104f593929190610d18565b60405180910390fd5b61050c84848484035f610603565b5b50505050565b5f73ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff1603610583575f6040517f96c6fd1e00000000000000000000000000000000000000000000000000000000815260040161057a9190610d4d565b60405180910390fd5b5f73ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff16036105f3575f6040517fec442f050000000000000000000000000000000000000000000000000000000081526004016105ea9190610d4d565b60405180910390fd5b6105fe8383836107d2565b505050565b5f73ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff1603610673575f6040517fe602df0500000000000000000000000000000000000000000000000000000000815260040161066a9190610d4d565b60405180910390fd5b5f73ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff16036106e3575f6040517f94280d620000000000000000000000000000000000000000000000000000000081526004016106da9190610d4d565b60405180910390fd5b8160015f8673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f205f8573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f208190555080156107cc578273ffffffffffffffffffffffffffffffffffffffff168473ffffffffffffffffffffffffffffffffffffffff167f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925846040516107c39190610ba6565b60405180910390a35b50505050565b5f73ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff1603610822578060025f8282546108169190610d93565b925050819055506108f0565b5f805f8573ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f20549050818110156108ab578381836040517fe450d38c0000000000000000000000000000000000000000000000000000000081526004016108a293929190610d18565b60405180910390fd5b8181035f808673ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f2081905550505b5f73ffffffffffffffffffffffffffffffffffffffff168273ffffffffffffffffffffffffffffffffffffffff1603610937578060025f8282540392505081905550610981565b805f808473ffffffffffffffffffffffffffffffffffffffff1673ffffffffffffffffffffffffffffffffffffffff1681526020019081526020015f205f82825401925050819055505b8173ffffffffffffffffffffffffffffffffffffffff168373ffffffffffffffffffffffffffffffffffffffff167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef836040516109de9190610ba6565b60405180910390a3505050565b5f81519050919050565b5f82825260208201905092915050565b5f5b83811015610a22578082015181840152602081019050610a07565b5f8484015250505050565b5f601f19601f8301169050919050565b5f610a47826109eb565b610a5181856109f5565b9350610a61818560208601610a05565b610a6a81610a2d565b840191505092915050565b5f6020820190508181035f830152610a8d8184610a3d565b905092915050565b5f80fd5b5f73ffffffffffffffffffffffffffffffffffffffff82169050919050565b5f610ac282610a99565b9050919050565b610ad281610ab8565b8114610adc575f80fd5b50565b5f81359050610aed81610ac9565b92915050565b5f819050919050565b610b0581610af3565b8114610b0f575f80fd5b50565b5f81359050610b2081610afc565b92915050565b5f8060408385031215610b3c57610b3b610a95565b5b5f610b4985828601610adf565b9250506020610b5a85828601610b12565b9150509250929050565b5f8115159050919050565b610b7881610b64565b82525050565b5f602082019050610b915f830184610b6f565b92915050565b610ba081610af3565b82525050565b5f602082019050610bb95f830184610b97565b92915050565b5f805f60608486031215610bd657610bd5610a95565b5b5f610be386828701610adf565b9350506020610bf486828701610adf565b9250506040610c0586828701610b12565b9150509250925092565b5f60ff82169050919050565b610c2481610c0f565b82525050565b5f602082019050610c3d5f830184610c1b565b92915050565b5f60208284031215610c5857610c57610a95565b5b5f610c6584828501610adf565b91505092915050565b5f8060408385031215610c8457610c83610a95565b5b5f610c9185828601610adf565b9250506020610ca285828601610adf565b9150509250929050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52602260045260245ffd5b5f6002820490506001821680610cf057607f821691505b602082108103610d0357610d02610cac565b5b50919050565b610d1281610ab8565b82525050565b5f606082019050610d2b5f830186610d09565b610d386020830185610b97565b610d456040830184610b97565b949350505050565b5f602082019050610d605f830184610d09565b92915050565b7f4e487b71000000000000000000000000000000000000000000000000000000005f52601160045260245ffd5b5f610d9d82610af3565b9150610da883610af3565b9250828201905080821115610dc057610dbf610d66565b5b9291505056fea2646970667358221220b4e22d489c5c118927538af7055c19e26d44361c7a7dd46844f7a556469d3d6b64736f6c63430008140033"  # Replace with actual bytecode
ERC721_BYTECODE = "0x608060405234801561001057600080fd5b506040516108..."  # Replace with actual bytecode
ERC1155_BYTECODE = "0x608060405234801561001057600080fd5b506040516109..."  # Replace with actual bytecode

# Initialize Alith Agent
agent = Agent(
    name="Telegram Bot Agent",
    model="gpt-4", 
    preamble="""You are an advanced AI assistant built by [Alith](https://github.com/0xLazAI/alith).""",
)

# Initialize Telegram Bot
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
app = Application.builder().token(bot_token).build()

# Store user state for multi-step deployments
user_states = {}

def is_valid_address(address: str) -> bool:
    """Validate Ethereum address format"""
    return address and len(address) == 42 and address.startswith('0x') and all(c in '0123456789abcdefABCDEF' for c in address[2:])

async def check_balance(contract_address: str, wallet_address: str) -> str:
    try:
        # Validate addresses
        if not is_valid_address(contract_address) or not is_valid_address(wallet_address):
            return "❌ Invalid address format. Addresses should be 42 characters long and start with '0x'"

        # Create contract instance
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(contract_address),
            abi=json.loads(ERC20_ABI)
        )
        
        # Get token info
        try:
            symbol = contract.functions.symbol().call()
            decimals = contract.functions.decimals().call()
            name = contract.functions.name().call()
            total_supply = contract.functions.totalSupply().call()
        except Exception as e:
            return f"❌ Error reading token information: {str(e)}"
        
        # Get balance
        balance = contract.functions.balanceOf(
            Web3.to_checksum_address(wallet_address)
        ).call()
                
        return (
            f"💰 Token Balance Report\n\n"
            f"Token Name: {name}\n"
            f"Symbol: {symbol}\n"
            f"Total Supply: {total_supply} {symbol}\n\n"
            f"Wallet: {wallet_address}\n"
            f"Balance: {balance} {symbol}\n\n"
            f"🔍 View on Explorer:\n"
            f"Token: {METIS_SEPOLIA_CONFIG['explorer_url']}/token/{contract_address}\n"
            f"Wallet: {METIS_SEPOLIA_CONFIG['explorer_url']}/address/{wallet_address}"
        )
    
    except Exception as e:
        return f"❌ Error checking balance: {str(e)}"

def show_token_deployment_options(chat_id: int) -> InlineKeyboardMarkup:
    """Create inline keyboard with token deployment options"""
    keyboard = [
        [
            InlineKeyboardButton("Deploy ERC20 Token", callback_data="deploy_erc20"),
            InlineKeyboardButton("Deploy ERC721 NFT", callback_data="deploy_erc721")
        ],
        [
            InlineKeyboardButton("Deploy ERC1155 Multi-Token", callback_data="deploy_erc1155"),
            InlineKeyboardButton("Cancel", callback_data="cancel_deploy")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

async def handle_callback_query(update: Update, context: CallbackContext) -> None:
    """Handle callback queries from inline keyboards"""
    query = update.callback_query
    chat_id = update.effective_chat.id
    
    # Always answer the callback query to remove the loading indicator
    await query.answer()
    
    if query.data == "cancel_deploy":
        await query.edit_message_text("Token deployment cancelled.")
        if chat_id in user_states:
            del user_states[chat_id]
        return
    
    if query.data.startswith("deploy_erc"):
        token_type = query.data.split("_")[1].upper()
        user_states[chat_id] = {
            "deploying": True,
            "token_type": token_type,
            "step": "get_wallet"
        }
        
        await query.edit_message_text(
            f"Let's deploy your {token_type} token!\n\n"
            f"Please provide your wallet address that will own the token:"
        )
        return
    
    # Handle other callback queries if needed

async def deploy_token(chat_id: int, token_type: str, params: dict) -> str:
    """Deploy a token based on type and parameters"""
    try:
        # Get private key from environment or user input (securely)
        private_key = os.getenv("DEPLOYER_PRIVATE_KEY")
        if not private_key:
            return "❌ Deployer private key not found in environment variables"
        
        # Create account from private key
        account = Account.from_key(private_key)
        
        # Get transaction parameters
        tx_params = {
            'from': account.address,
            'nonce': w3.eth.get_transaction_count(account.address),
            'gasPrice': w3.eth.gas_price,
            'chainId': METIS_SEPOLIA_CONFIG['chain_id']
        }
        
        contract_data = None
        constructor_args = None
        
        if token_type == "ERC20":
            contract = w3.eth.contract(abi=json.loads(ERC20_ABI), bytecode=ERC20_BYTECODE)
            constructor_args = [
                params['name'],
                params['symbol'],
                int(float(params['supply'])),  # Convert to smallest units
                Web3.to_checksum_address(params['owner'])
            ]
        elif token_type == "ERC721":
            contract = w3.eth.contract(abi=json.loads(ERC721_ABI), bytecode=ERC721_BYTECODE)
            constructor_args = [
                params['name'],
                params['symbol'],
                params['base_uri']
            ]
        elif token_type == "ERC1155":
            contract = w3.eth.contract(abi=json.loads(ERC1155_ABI), bytecode=ERC1155_BYTECODE)
            constructor_args = [params['uri']]
        
        # Build constructor transaction
        contract_tx = contract.constructor(*constructor_args).build_transaction(tx_params)
        
        # Estimate gas
        gas_estimate = w3.eth.estimate_gas(contract_tx)
        contract_tx['gas'] = gas_estimate
        
        # Sign transaction
        signed_tx = w3.eth.account.sign_transaction(contract_tx, private_key)
        
        # Send transaction - Using the correct attribute for Web3.py
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for transaction receipt
        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        
        contract_address = tx_receipt.contractAddress
        
        return (
            f"✅ {token_type} Token Deployed Successfully!\n\n"
            f"Contract Address: {contract_address}\n"
            f"Transaction Hash: {tx_hash.hex()}\n\n"
            f"🔍 View on Explorer:\n"
            f"{METIS_SEPOLIA_CONFIG['explorer_url']}/address/{contract_address}\n"
            f"{METIS_SEPOLIA_CONFIG['explorer_url']}/tx/{tx_hash.hex()}"
        )
    
    except Exception as e:
        return f"❌ Error deploying {token_type} token: {str(e)}"
        
async def process_deployment_steps(update: Update, context: CallbackContext, chat_id: int, user_state: dict) -> None:
    """Process token deployment steps based on user state"""
    token_type = user_state["token_type"]
    step = user_state["step"]
    message_text = update.message.text.strip()
    
    if step == "get_wallet":
        if not is_valid_address(message_text):
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Invalid wallet address. Please provide a valid Ethereum address starting with 0x."
            )
            return
        
        user_state["owner"] = message_text
        user_state["step"] = "get_name"
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=f"Great! Now enter a name for your {token_type} token:"
        )
    
    elif step == "get_name":
        user_state["name"] = message_text
        user_state["step"] = "get_symbol"
        
        await context.bot.send_message(
            chat_id=chat_id,
            text="Now enter a symbol for your token (e.g. BTC, ETH):"
        )
    
    elif step == "get_symbol":
        user_state["symbol"] = message_text
        
        if token_type == "ERC20":
            user_state["step"] = "get_supply"
            await context.bot.send_message(
                chat_id=chat_id,
                text="Enter the initial supply for your token (e.g. 1000000):"
            )
        elif token_type == "ERC721":
            user_state["step"] = "get_base_uri"
            await context.bot.send_message(
                chat_id=chat_id,
                text="Enter the base URI for your NFT metadata (e.g. https://example.com/metadata/):"
            )
        elif token_type == "ERC1155":
            user_state["step"] = "get_uri"
            await context.bot.send_message(
                chat_id=chat_id,
                text="Enter the URI for your multi-token metadata (e.g. https://example.com/metadata/{id}.json):"
            )
    
    elif step == "get_supply":
        try:
            supply = float(message_text)
            user_state["supply"] = message_text
            user_state["step"] = "confirm"
            
            # Show confirmation
            await context.bot.send_message(
                chat_id=chat_id,
                text=(
                    f"📋 Deployment Summary (ERC20):\n\n"
                    f"Name: {user_state['name']}\n"
                    f"Symbol: {user_state['symbol']}\n"
                    f"Supply: {user_state['supply']}\n"
                    f"Owner: {user_state['owner']}\n\n"
                    f"Type 'confirm' to deploy or 'cancel' to abort."
                )
            )
        except ValueError:
            await context.bot.send_message(
                chat_id=chat_id,
                text="❌ Invalid supply. Please enter a valid number."
            )
    
    elif step == "get_base_uri" or step == "get_uri":
        uri_key = "base_uri" if step == "get_base_uri" else "uri"
        user_state[uri_key] = message_text
        user_state["step"] = "confirm"
        
        # Show confirmation
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"📋 Deployment Summary ({token_type}):\n\n"
                f"Name: {user_state['name']}\n"
                f"Symbol: {user_state['symbol']}\n"
                f"{uri_key.replace('_', ' ').title()}: {user_state[uri_key]}\n"
                f"Owner: {user_state['owner']}\n\n"
                f"Type 'confirm' to deploy or 'cancel' to abort."
            )
        )
    
    elif step == "confirm":
        if message_text.lower() == "confirm":
            # Send initial status
            status_message = await context.bot.send_message(
                chat_id=chat_id,
                text=f"🔄 Deploying your {token_type} token... Please wait."
            )
            
            # Deploy token
            params = {
                "owner": user_state["owner"],
                "name": user_state["name"],
                "symbol": user_state["symbol"]
            }
            
            if "supply" in user_state:
                params["supply"] = user_state["supply"]
            if "base_uri" in user_state:
                params["base_uri"] = user_state["base_uri"]
            if "uri" in user_state:
                params["uri"] = user_state["uri"]
            
            result = await deploy_token(chat_id, token_type, params)
            
            # Update with result
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_message.message_id,
                text=result
            )
            
            # Clear user state
            del user_states[chat_id]
        
        elif message_text.lower() == "cancel":
            await context.bot.send_message(
                chat_id=chat_id,
                text="Token deployment cancelled."
            )
            del user_states[chat_id]
        
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="Please type 'confirm' to proceed with deployment or 'cancel' to abort."
            )

async def handle_message(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    message_text = update.message.text.lower()
    
    # Check if user is in deployment flow
    if chat_id in user_states and user_states[chat_id].get("deploying"):
        await process_deployment_steps(update, context, chat_id, user_states[chat_id])
        return
    
    # Handle greetings
    if message_text in ["hi", "hello", "hey", "hola", "greetings"]:
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                "👋 Hello! Would you like to deploy a token on Metis Sepolia?"
            ),
            reply_markup=show_token_deployment_options(chat_id)
        )
        return
    
    # Handle balance command
    if message_text.startswith('/balance'):
        await check_balance_command(update, context)
    elif "check balance" in message_text.lower() or "show balance" in message_text.lower():
        try:
            # Find addresses in the message
            words = message_text.split()
            addresses = [word for word in words if is_valid_address(word)]
            
            if len(addresses) < 2:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text=(
                        "Please provide both contract and wallet addresses.\n"
                        "Examples:\n"
                        "1. Check balance for contract 0x123... wallet 0x456...\n"
                        "2. /balance 0x123... 0x456..."
                    )
                )
                return
            
            contract_address = addresses[0]
            wallet_address = addresses[1]
            
            # Send initial status
            status_message = await context.bot.send_message(
                chat_id=chat_id,
                text="🔍 Checking token balance..."
            )
            
            # Check balance
            result = await check_balance(contract_address, wallet_address)
            
            # Update with result
            await context.bot.edit_message_text(
                chat_id=chat_id,
                message_id=status_message.message_id,
                text=result
            )
            
        except Exception as e:
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"❌ Error: {str(e)}\n\nPlease use the format:\nCheck balance for contract 0x123... wallet 0x456..."
            )
    else:
        # Handle other messages with AI agent
        response = agent.prompt(update.message.text)
        await context.bot.send_message(chat_id=chat_id, text=response)

async def check_balance_command(update: Update, context: CallbackContext):
    try:
        params = update.message.text.split()
        if len(params) != 3:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=(
                    "Please provide contract and wallet address:\n"
                    "/balance <contract_address> <wallet_address>"
                )
            )
            return
        
        _, contract_address, wallet_address = params
        
        # Send initial status
        status_message = await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="🔍 Checking token balance..."
        )
        
        # Check balance
        result = await check_balance(contract_address, wallet_address)
        
        # Update with result
        await context.bot.edit_message_text(
            chat_id=update.effective_chat.id,
            message_id=status_message.message_id,
            text=result
        )
        
    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ Error: {str(e)}"
        )

# Add handlers
app.add_handler(CommandHandler("balance", handle_message))
app.add_handler(CallbackQueryHandler(handle_callback_query))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# Start bot
if __name__ == "__main__":
    print(f"🤖 Bot starting on {METIS_SEPOLIA_CONFIG['name']}...")
    print("Available commands:")
    print("1. /balance <contract_address> <wallet_address>")
    print("2. Natural language: 'Check balance for contract 0x... wallet 0x...'")
    print("3. Say 'hi' or 'hello' to get token deployment options")
    app.run_polling()
