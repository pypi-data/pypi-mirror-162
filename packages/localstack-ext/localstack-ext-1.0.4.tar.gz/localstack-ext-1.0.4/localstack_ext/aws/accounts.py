import logging,re,threading
from typing import Any,Callable
from localstack import config as localstack_config
from localstack.aws.accounts import REQUEST_CTX_TLS,get_aws_account_id,get_default_account_id
from localstack.constants import LS_LOG_TRACE_INTERNAL
from localstack.utils.patch import patch
def _patch_moto_backend_dict():
	C='[0-9]+';import moto as A
	@patch(A.core.utils.BackendDict.__getitem__)
	def B(__getitem__,self,account_id_or_region):
		D=account_id_or_region;B=self
		if re.match(C,D):B._create_account_specific_backend(get_aws_account_id());return super(A.core.utils.BackendDict,B).__getitem__(get_aws_account_id())
		else:E=D;return B[get_aws_account_id()][E]
	@patch(A.core.utils.BackendDict.__contains__)
	def D(__contains__,self,account_id_or_region):
		B=account_id_or_region;A=self
		if re.match(C,B):A._create_account_specific_backend(get_aws_account_id());return True
		else:D=B;A._create_account_specific_backend(get_aws_account_id());return D in A[get_aws_account_id()]
def _patch_account_id_resolver():
	import localstack as A
	def B():
		try:return REQUEST_CTX_TLS.account_id
		except AttributeError:
			if localstack_config.LS_LOG and localstack_config.LS_LOG==LS_LOG_TRACE_INTERNAL:logging.debug('No Account ID in thread-local storage for thread %s',threading.current_thread().ident)
			return get_default_account_id()
	A.aws.accounts.account_id_resolver=B
def _patch_get_account_id_from_access_key_id():
	from localstack.aws import accounts as A
	def B(access_key_id):A=C(access_key_id);REQUEST_CTX_TLS.account_id=A;return A
	C=A.get_account_id_from_access_key_id;A.get_account_id_from_access_key_id=B