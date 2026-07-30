# Open-source release plan

This public plan covers only Vidux itself. It deliberately excludes provider
accounts, private repositories, worker receipts, personal paths, session
identifiers, costs, and unpublished portfolio decisions.

## Outcome

Keep Vidux a small, local-first plan/proof/resume layer that complements coding
agents instead of competing with their execution engines.

## Constraints

- Public examples use synthetic identities and repository-neutral paths.
- Release claims require exact-tag tests, package verification, and a current
  public-boundary scan.
- Provider routing, authentication, billing, and private fleet operations stay
  outside this repository.
- No release may claim execution, scheduling, proof authentication, or remote
  worker control that Vidux does not provide.

## Tasks

- [completed] Publish the provider-neutral Outcome / Ask / Steer contract.
- [completed] Require test, package, secret-scan, and public-boundary gates.
- [completed] Remove private operational history from the maintained public
  source and package surfaces.
- [pending] Evaluate future changes against stranger usability and the narrow
  plan/proof/resume contract before expanding the product.

## Proof

- `npm run verify`
- `npm run release:verify`
- `npm run test:e2e`
- hosted CI, CodeQL, secret scanning, and dependency alerts

The repository history is durable evidence, but it is not a license to append
private campaign logs here. Detailed portfolio operations belong in their
own non-public authority.
